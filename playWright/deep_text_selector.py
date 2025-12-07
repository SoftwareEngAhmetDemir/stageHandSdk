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

async def deep_text_fill(page: Page, text: str, value: str):
    """
    Fill an input element by finding the input nearest to the text.
    Safe if no input found.
    """
    try:
        js = """
        (text, value) => {
            text = text.toLowerCase();
            const inputs = [...document.querySelectorAll('input, textarea')];
            if (!inputs.length) return null;
            const elements = Array.from(inputs);
            for (const el of elements) {
                const label = el.closest('label');
                if (label && label.innerText.toLowerCase().includes(text)) {
                    el.value = value;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    return el;
                }
            }
            // fallback: fill first input if text not matched
            const firstInput = inputs[0];
            firstInput.value = value;
            firstInput.dispatchEvent(new Event('input', { bubbles: true }));
            return firstInput;
        }
        """
        filled = await page.evaluate(js, text, value)
        if not filled:
            print(f"[Warning] No input found for '{text}', skipping fill.")
    except Exception as e:
        print(f"[Warning] Error filling input '{text}': {e}")
