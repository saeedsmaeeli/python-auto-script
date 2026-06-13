import requests
from bs4 import BeautifulSoup
import time
import json


URL = "https://tokenomist.ai/humidifi"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


# -----------------------------
# Retry Wrapper (fast + stable)
# -----------------------------
def fetch_with_retry(url, retries=5, timeout=10, backoff=1.5):
    session = requests.Session()

    for i in range(retries):
        try:
            response = session.get(url, headers=HEADERS, timeout=timeout)

            if response.status_code == 200:
                return response.text

            print(f"[WARN] Status {response.status_code}, retry {i+1}/{retries}")

        except requests.RequestException as e:
            print(f"[ERROR] {e}, retry {i+1}/{retries}")

        time.sleep(backoff * (i + 1))

    return None


# -----------------------------
# Extractor
# -----------------------------
def extract_metrics(html):
    soup = BeautifulSoup(html, "html.parser")

    data = {}

    # همه بلوک‌های متریک
    blocks = soup.find_all("div", class_="flex h-4.5 min-h-4.5 flex-1 items-center justify-between")

    for block in blocks:
        label_el = block.find("div", class_="text-[13px]")
        value_el = block.find_all("div", class_="text-[13px]")

        if not label_el or len(value_el) < 2:
            continue

        label = label_el.get_text(strip=True)
        value = value_el[1].get_text(strip=True)

        if "Reported Market Cap" in label:
            data["reported_market_cap"] = value

        elif "Adjusted Market Cap" in label:
            data["adjusted_market_cap"] = value

        elif "Fully Diluted Value" in label:
            data["fully_diluted_value"] = value

    # Float % (ساختار متفاوت grid)
    float_block = soup.find("div", class_="grid grid-cols-[52px_1fr_min-content] items-center gap-x-2")
    if float_block:
        percent = float_block.find_all("div")[-1].get_text(strip=True)
        data["float_percent"] = percent

    return data


# -----------------------------
# Main
# -----------------------------
def main():
    html = fetch_with_retry(URL)

    if not html:
        print("Failed to fetch page after retries")
        return

    result = extract_metrics(html)

    print(json.dumps(result, indent=4, ensure_ascii=False))


if name == "main":
    main()
