import requests
import time

url = "https://api.coingecko.com/api/v3/global"

def get_btc_dominance():
    for i in range(3):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            btc_dom = data["data"]["market_cap_percentage"]["btc"]

            return btc_dom

        except requests.exceptions.RequestException as e:
            print(f"retry {i+1} failed:", e)
            time.sleep(2)

    return None


btc_dom = get_btc_dominance()

if btc_dom is None:
    print("❌ error")
    exit()

# -------------------------
# insight
# -------------------------
if btc_dom >= 55:
    insight = "تمرکز بازار روی بیت‌کوین"
elif btc_dom > 50:
    insight = "بازار متعادل"
else:
    insight = "تمایل بازار به آلت‌کوین‌ها"

print("BTC Dominance:", btc_dom)
print("Insight:", insight)

# -------------------------
# send to PHP
# -------------------------
payload = {
    "title": "BTC Dominance",
    "value": btc_dom,
    "insight": insight
}

php_url = "http://bazarpulse.ir/receiver_dominance.php"

response = requests.post(php_url, json=payload)

print("PHP Response:", response.text)
