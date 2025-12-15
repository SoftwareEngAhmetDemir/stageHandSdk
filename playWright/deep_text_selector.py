from typing import Optional
from pathlib import Path

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    ElementHandle,
)

# ------------------------------------------------------------
# Load shared JS helpers
# ------------------------------------------------------------

JS_PATH = Path(__file__).parent / "../js/index.js"


# ------------------------------------------------------------
# Context / Page bootstrap
# ------------------------------------------------------------

async def new_context_with_deep_text(browser: Browser, **kwargs):
    """
    Creates a new browser context and page.
    Injects deepText JS helpers globally.
    Returns (context, page)
    """
    context: BrowserContext = await browser.new_context(**kwargs)

    # Inject JS once for all pages in this context
    await context.add_init_script(path=str(JS_PATH))

    page: Page = await context.new_page()
    return context, page


# ------------------------------------------------------------
# Text / Input handlers
# ------------------------------------------------------------

async def deep_text_fill(page: Page, label_text: str, value: str) -> bool:
    """
    Fill input or textarea using deepText heuristics.
    """
    try:
        handle = await page.evaluate_handle(
            "(label) => window.deepText.findInputByLabel(label)",
            label_text,
        )

        el: Optional[ElementHandle] = handle.as_element() if handle else None
        if not el:
            print(f"[Warning] Input not found: '{label_text}'")
            return False

        await el.fill("")
        await el.type(value, delay=50)
        return True

    except Exception as e:
        print(f"[Warning] Error filling '{label_text}': {e}")
        return False


async def deep_text_checkbox(page: Page, label_text: str, value: bool) -> bool:
    """
    Safely toggle checkbox by label text.
    """
    try:
        return await page.evaluate(
            "(args) => window.deepText.toggleCheckbox(args.label, args.checked)",
            {"label": label_text, "checked": value},
        )
    except Exception:
        return False


async def deep_text_radio_or_select(page: Page, label: str, option: str) -> bool:
    """
    Try selecting radio button or select dropdown.
    """
    try:
        # Radio buttons
        if await page.evaluate(
            "(option) => window.deepText.selectRadio(option)",
            option,
        ):
            print(f"[OK] Radio selected: {option}")
            return True

        # Select dropdown
        if await page.evaluate(
            "(args) => window.deepText.selectDropdown(args.label, args.option)",
            {"label": label, "option": option},
        ):
            print(f"[OK] Select chosen: {label} → {option}")
            return True

    except Exception:
        pass

    print(f"[Warning] Could not select '{option}' for '{label}'")
    return False


# ------------------------------------------------------------
# Universal form auto-filler
# ------------------------------------------------------------

async def deep_text_auto_fill(page: Page, instructions: dict):
    """
    Universal form filler.

    Example:
    instructions = {
        "First name": "Ahmet",
        "Surname": "Demir",
        "Gender": "Female",
        "Day": "20",
        "Month": "Oct",
        "Year": "1990",
        "Mobile": "1234567890",
        "Accept Terms": True,
        "Sign Up": "@click"
    }
    """
    for field, value in instructions.items():
        try:
            # ---------------- CLICK ----------------

            if isinstance(value, str) and value.strip().lower() == "@click":
                await page.wait_for_timeout(3000)
                clicked = await page.evaluate(
                    "(text) => window.deepText.clickByText(text)",
                    field,
                )

                if clicked:
                    print(f"[OK] Clicked: {field}")
                else:
                    print(f"[Warning] Could not click '{field}'")
                continue

            # ---------------- CHECKBOX ----------------
            if isinstance(value, bool):
                success = await deep_text_checkbox(page, field, value)
                if not success:
                    print(f"[Warning] Checkbox not found: '{field}'")
                continue

            # ---------------- RADIO / SELECT / INPUT ----------------
            str_value = str(value)

            selected = await deep_text_radio_or_select(
                page,
                field,
                str_value,
            )

            if not selected:
                await deep_text_fill(page, field, str_value)

        except Exception as e:
            print(f"[Warning] Failed for '{field}': {e}")
