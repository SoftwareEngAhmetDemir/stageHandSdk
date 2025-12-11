from typing import Optional
from playwright.async_api import Browser, BrowserContext, Page, ElementHandle

async def new_context_with_deep_text(browser: Browser, **kwargs):
    """
    Creates a new context and a new page.
    Returns a tuple: (context, page)
    """
    context: BrowserContext = await browser.new_context(**kwargs)
    page: Page = await context.new_page()
    return context, page



async def deep_text_fill(page: Page, label_text: str, value: str):
    """
    Fill an input/textarea by:
      1. aria-label
      2. placeholder
      3. linked <label for="">
      4. closest visible input/textarea to matching text anywhere on page
    Stops at first successful fill.
    Returns True if filled, False otherwise.
    """
    try:
        handle = await page.evaluate_handle(
            """
            ({ label }) => {
                const normalize = s => (s||'').trim().toLowerCase();
                const targetLabel = normalize(label);

                const inputs = [...document.querySelectorAll('input, textarea')].filter(i => i.offsetParent !== null);

                // 1) Match aria-label or placeholder
                for (const el of inputs) {
                    if (normalize(el.getAttribute('aria-label')) === targetLabel) return el;
                    if (normalize(el.placeholder) === targetLabel) return el;
                    if (el.id) {
                        const lbl = document.querySelector(`label[for="${el.id}"]`);
                        if (lbl && normalize(lbl.innerText) === targetLabel) return el;
                    }
                }

                // 2) Find closest input/textarea to text anywhere on page
                const textElements = Array.from(document.querySelectorAll('body *')).filter(el => {
                    return (el.innerText || '').trim().toLowerCase().includes(targetLabel);
                });

                if (textElements.length === 0) return null;

                function domDistance(a, b) {
                    let count = 0, node = b;
                    while (node && node !== document.body) {
                        if (a.contains(node) || a === node) return count;
                        node = node.parentElement;
                        count++;
                    }
                    return Infinity;
                }

                let best = null, minDistance = Infinity;
                for (const te of textElements) {
                    for (const inp of inputs) {
                        const dist = domDistance(te, inp);
                        if (dist < minDistance) {
                            minDistance = dist;
                            best = inp;
                        }
                    }
                }

                return best;
            }
            """,
            {"label": label_text},
        )

        el: Optional[ElementHandle] = handle.as_element() if handle else None
        if el:
            await el.fill("")  # clear previous value
            await el.type(value, delay=50)
            return True

        print(f"[Warning] Could not find input/textarea for '{label_text}'")
        return False
    except Exception as e:
        print(f"[Warning] Error filling '{label_text}': {e}")
        return False



async def deep_text_checkbox(page: Page, label_text: str, value: bool):
    """Check or uncheck checkbox safely by label text."""
    try:
        result = await page.evaluate(
            """
            ({ label, checked }) => {
                const boxes = [...document.querySelectorAll('input[type="checkbox"]')];
                for (const b of boxes) {
                    const lbl = b.closest('label');
                    if ((lbl?.innerText || '').toLowerCase().includes(label.toLowerCase())) {
                        b.checked = checked;
                        b.dispatchEvent(new Event('change', { bubbles: true }));
                        return true;
                    }
                }
                return false;
            }
            """,
            {"label": label_text, "checked": value},
        )
        return result
    except Exception:
        return False

async def deep_text_radio_or_select(page: Page, label: str, option: str):
    """
    GENERAL input selector.
    Tries sequentially with short-circuit:
        1. Radio buttons
        2. Single/multiple selects via label or nearby text
    Stops at the first successful selection.
    """
    label_norm = label.strip().lower()
    opt_norm = option.strip().lower()

    # ---------------- Radio buttons ----------------
    try:
        radio_clicked = await page.evaluate(
            """
            ({ option }) => {
                const t = option.toLowerCase().trim();
                const radios = [...document.querySelectorAll('input[type="radio"]')];

                function normalize(s) { return (s||'').toLowerCase().trim(); }
                function labelText(radio) {
                    const lbl = radio.closest('label') || (radio.id ? document.querySelector(`label[for="${radio.id}"]`) : null);
                    if (lbl) return normalize(lbl.innerText);
                    const parent = radio.closest('div, span, section');
                    if (parent) return normalize(parent.innerText);
                    return '';
                }

                for (const r of radios) {
                    if (r.value && normalize(r.value) === t) { (r.closest('label')||r).click(); return true; }
                }
                for (const r of radios) {
                    const text = labelText(r);
                    if (text.split(' ').includes(t)) { (r.closest('label')||r).click(); return true; }
                }
                return false;
            }
            """,
            {"option": opt_norm},
        )
        if radio_clicked:
            print(f"[OK] Radio selected: {option}")
            return True
    except Exception:
        pass

    # ---------------- Select dropdowns ----------------
    try:
        select_clicked = await page.evaluate(
            """
            ({ label, option }) => {
                const tLabel = label.toLowerCase().trim();
                const tOption = option.toLowerCase().trim();
                const selects = [...document.querySelectorAll("select")];

                function normalize(s) { return (s||'').toLowerCase().trim(); }

                for (const sel of selects) {
                    try {
                        // Label[for] or aria-label/title/name match
                        const meta = (sel.getAttribute("aria-label")||sel.getAttribute("title")||sel.getAttribute("name")||'').toLowerCase();
                        const lbl = sel.id ? document.querySelector(`label[for="${sel.id}"]`) : null;
                        if ((meta.includes(tLabel)) || (lbl && (lbl.innerText||'').toLowerCase().includes(tLabel))) {
                            const match = [...sel.options].find(o => (o.textContent||'').toLowerCase().includes(tOption) || (o.value||'').toLowerCase()===tOption);
                            if (match) { sel.value = match.value; sel.dispatchEvent(new Event("input",{bubbles:true})); sel.dispatchEvent(new Event("change",{bubbles:true})); return true; }
                        }
                    } catch {}
                }
                return false;
            }
            """,
            {"label": label_norm, "option": opt_norm},
        )
        if select_clicked:
            print(f"[OK] Select list: {label} → {option}")
            return True
    except Exception:
        pass

    print(f"[Warning] Could not select '{option}' for '{label}'")
    return False

async def deep_text_auto_fill(page: Page, instructions: dict):
    """
    Universal form filler.
    instructions = {
        "First name": "Ahmet",
        "Surname": "Demir",
        "Gender": "Female",
        "Day": "20",
        "Month": "Oct",
        "Year": "1990",
        "Mobile": "1234567890",
        "Password": "SecureP@ssw0rd!",
        "Sign Up": "@click"
    }
    """
    for field, value in instructions.items():
        try:
            # Click button if value="@click"
            if isinstance(value, str) and value.strip().lower() == "@click":
                from playwright.async_api import TimeoutError
                try:
                    handle = await page.query_selector(f"text={field}")
                    if handle:
                        await handle.click()
                        continue
                except TimeoutError:
                    print(f"[Warning] Could not click button '{field}'")
                    continue

            # Boolean -> checkbox
            if isinstance(value, bool):
                await deep_text_checkbox(page, field, value)
                continue

            # For strings/numbers: try radio/select first, fallback to input
            str_value = str(value)
            success = await deep_text_radio_or_select(page, field, str_value)
            if not success:
                await deep_text_fill(page, field, str_value)

        except Exception as e:
            print(f"[Warning] Failed to fill '{field}': {e}")
