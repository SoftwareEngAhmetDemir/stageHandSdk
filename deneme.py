import asyncio
from playwright.async_api import async_playwright
from playWright.deep_text_selector import new_context_with_deep_text, deep_text_fill, deep_text_click

async def main():
    async with async_playwright() as p:
        # browser = await p.chromium.launch(headless=False)
        # context, page = await new_context_with_deep_text(browser)
        # await page.goto("https://www.google.com")
        # await page.wait_for_load_state()

        # # Try to fill the search input safely
        # await deep_text_fill(page, "Search or type a URL", "red apple")
        # # Try to click the search button safely
        # await deep_text_click(page, "Google Search")

        # # You can continue automation here safely
        # # For example, click the first result if exists
        # await deep_text_click(page, "red apple")  # Example: click first result

        # await browser.close()
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://www.facebook.com/reg/")
        await page.wait_for_load_state()

        # Fill the first name field
        await page.wait_for_selector('input[name="firstname"]')
        await page.fill('input[name="firstname"]', "Ahmet")

        # Fill the last name field
        await page.wait_for_selector('input[name="lastname"]')
        await page.fill('input[name="lastname"]', "Demir")
        await asyncio.sleep(50)  # Pause to see the filled form
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
