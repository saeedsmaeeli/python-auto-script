import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


async def fetch_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        page = await browser.new_page()

        try:
            await page.goto(
                "https://tokenomist.ai/humidifi",
                wait_until="domcontentloaded",
                timeout=60000
            )

            await page.wait_for_selector(
                "div.flex.flex-auto.flex-col.justify-between.gap-y-4",
                timeout=30000
            )

            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")

            container = soup.find(
                "div",
                class_="flex flex-auto flex-col justify-between gap-y-4"
            )

            if container:
                rows = container.find_all(
                    "div",
                    class_="flex h-4.5 min-h-4.5 flex-1 items-center justify-between"
                )

                for row in rows:
                    label = row.find("div", class_="tracking-[-0.12px]")
                    value = row.find("div", class_="text-[13px] leading-[16px] text-black-primary")

                    if label and value:
                        print(f"{label.text.strip()}: {value.text.strip()}")
            else:
                print("Container not found")

        except Exception as e:
            print(f"Error: {e}")

        finally:
            await browser.close()


if name == "main":
    asyncio.run(fetch_data())
