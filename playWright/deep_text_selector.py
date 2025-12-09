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

async def deep_text_locator(page: Page, text: str) -> Optional[ElementHandle]:
    """
    Returns the first element matching the given text (case-insensitive),
    including shadow DOM. Returns None if not found.
    """
    js = """
    (text) => {
        text = text.toLowerCase();
        function search(root) {
            let result = null;
            function recurse(node) {
                if (!node) return;
                const t = (node.innerText || node.placeholder || '').trim().toLowerCase();
                if (!result && t.includes(text)) result = node;
                if (node.children) [...node.children].forEach(recurse);
                if (node.shadowRoot) recurse(node.shadowRoot);
            }
            recurse(root);
            return result;
        }
        return search(document);
    }
    """
    handle = await page.evaluate_handle(js, text)
    return handle if handle else None

async def deep_text_click(page: Page, text: str):
    """Click the first element matching the deep-text selector. Safe if not found."""
    try:
        el_handle = await deep_text_locator(page, text)
        if el_handle:
            await el_handle.click()
        else:
            print(f"[Warning] Element '{text}' not found, skipping click.")
    except Exception as e:
        print(f"[Warning] Error clicking element '{text}': {e}")

async def deep_text_fill(page, text: str, value: str):
    """
    Fill an input or textarea by searching for visible text or placeholder on the page.
    Works with:
      - labels
      - div/span text
      - placeholder attributes
    """
    try:
        js = """
        (args) => {
            const targetText = args.text.toLowerCase();
            const value = args.value;

            // All inputs and textareas
            const inputs = [...document.querySelectorAll('input, textarea')];

            function getText(node) {
                if (!node) return '';
                return (node.innerText || node.placeholder || '').trim().toLowerCase();
            }

            function distance(a, b) {
                // Approximate DOM tree distance
                let count = 0;
                while (a && a !== document.body) {
                    if (a === b) return count;
                    a = a.parentElement;
                    count++;
                }
                return Infinity;
            }

            let bestInput = null;
            let bestScore = Infinity;

            for (const input of inputs) {
                // Check placeholder
                if (input.placeholder && input.placeholder.toLowerCase().includes(targetText)) {
                    bestInput = input;
                    break;
                }

                // Check nearest ancestor text nodes (labels, div, span)
                const allTexts = Array.from(document.querySelectorAll('label, div, span'));
                for (const t of allTexts) {
                    if (t.innerText.toLowerCase().includes(targetText)) {
                        const score = distance(input, t);
                        if (score < bestScore) {
                            bestScore = score;
                            bestInput = input;
                        }
                    }
                }
            }

            if (!bestInput && inputs.length) {
                bestInput = inputs[0];  // fallback to first input
            }

            if (bestInput) {
                bestInput.focus();
                bestInput.value = value;
                bestInput.dispatchEvent(new Event('input', { bubbles: true }));
                return true;
            }

            return false;
        }
        """
        filled = await page.evaluate(js, {"text": text, "value": value})
        if not filled:
            print(f"[Warning] No input found for '{text}', skipping fill.")
    except Exception as e:
        print(f"[Warning] Error filling input '{text}': {e}")
        
async def deep_text_radio(page, text: str):
    """
    Click a radio button (<input type="radio">) by exact visible text nearby.
    Works with:
      - radio inside <label>
      - label text linked via 'for'
      - div/span text nearby
    Safe if no matching radio found.
    """
    try:
        js = """
        (targetText) => {
            const targetTextLower = targetText.toLowerCase().trim();

            const radios = Array.from(document.querySelectorAll('input[type="radio"]'));

            function getText(node) {
                if (!node) return '';
                return (node.innerText || node.textContent || '').trim().toLowerCase();
            }

            function textMatches(nodeText, targetText) {
                // Match exact word to avoid substrings like 'Male' inside 'Female'
                nodeText = nodeText.toLowerCase().trim();
                const words = nodeText.split(/\s+/);
                return words.includes(targetText);
            }

            function distance(a, b) {
                let count = 0;
                let p = a;
                while (p && p !== document.body) {
                    if (p === b) return count;
                    p = p.parentElement;
                    count++;
                }
                return Infinity;
            }

            let bestRadio = null;
            let bestScore = Infinity;

            for (const radio of radios) {
                // 1. Check if the radio's value matches exactly
                if (radio.value && radio.value.toLowerCase().trim() === targetTextLower) {
                    bestRadio = radio;
                    break;
                }

                // 2. Check if radio is inside a label
                const parentLabel = radio.closest('label');
                if (parentLabel && textMatches(getText(parentLabel), targetTextLower)) {
                    bestRadio = radio;
                    break;
                }

                // 3. Check labels with 'for' attribute
                const linkedLabel = document.querySelector(`label[for="${radio.id}"]`);
                if (linkedLabel && textMatches(getText(linkedLabel), targetTextLower)) {
                    bestRadio = radio;
                    break;
                }

                // 4. Check nearby div/span/label elements
                const textNodes = Array.from(document.querySelectorAll('div, span, label'));
                for (const node of textNodes) {
                    if (textMatches(getText(node), targetTextLower)) {
                        const score = distance(radio, node);
                        if (score < bestScore) {
                            bestScore = score;
                            bestRadio = radio;
                        }
                    }
                }
            }

            if (bestRadio) {
                bestRadio.scrollIntoView({behavior: "smooth", block: "center"});
                bestRadio.click();
                return true;
            }

            return false;
        }
        """
        clicked = await page.evaluate(js, text)
        if not clicked:
            print(f"[Warning] No radio button found for '{text}', skipping click.")
    except Exception as e:
        print(f"[Warning] Error clicking radio button '{text}': {e}")
