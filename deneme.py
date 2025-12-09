import asyncio
from playwright.async_api import async_playwright
from playWright.deep_text_selector import new_context_with_deep_text, deep_text_fill, deep_text_click,deep_text_radio

# Safe wrappers to prevent crashes
async def safe_deep_text_fill(page, text, value):
    try:
        await deep_text_fill(page, text, value)
    except Exception as e:
        print(f"[Warning] Failed to fill '{text}': {e}")

async def safe_deep_text_click(page, text):
    try:
        await deep_text_click(page, text)
    except Exception as e:
        print(f"[Warning] Failed to click '{text}': {e}")

async def main():
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context, page = await new_context_with_deep_text(browser)

            # Navigate safely
            try:
                await page.goto("https://www.facebook.com/reg/", wait_until="load")
            except Exception as e:
                print(f"[Warning] Navigation failed: {e}")
                return

            # Fill the signup form
            await safe_deep_text_fill(page, "First name", "Ahmet")
            await safe_deep_text_fill(page, "Surname", "Demir")

           # Select gender using deep_text_radio
            await deep_text_radio(page, "male")
           

            # Click 'Sign Up' button
            await safe_deep_text_click(page, "Sign Up")

            print("Waiting 50 seconds before closing browser...")
            await asyncio.sleep(50)

    except Exception as e:
        print(f"[Warning] Unexpected error: {e}")
    finally:
        if browser:
            await browser.close()
        print("Browser closed safely.")

if __name__ == "__main__":
    asyncio.run(main())