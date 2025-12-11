import asyncio
from playwright.async_api import async_playwright
from playWright.deep_text_selector import (
    new_context_with_deep_text,
   deep_text_auto_fill
    
)

async def main():
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context, page = await new_context_with_deep_text(browser)

            try:
                await page.goto("https://www.facebook.com/reg/", wait_until="load")
            except Exception as e:
                print(f"[Warning] Navigation failed: {e}")
                return

            await deep_text_auto_fill(page, {
                "First name": "Ahmet",
                "Surname": "Demir",
                "Gender": "Female",
                "Day": "20",
                "Month": "Oct",
                "Year": "1990",
                "Mobile number or email address":"1234567890",
                "New password":"SecureP@ssw0rd!",
                "password":"SecureP@ssw0rd!",
                "Sign Up": "@click"
            })

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
