import requests
import json

# جلوگیری از استفاده از پروکسی سیستم (در GitHub Actions هم مشکلی ندارد)
PROXIES_OFF = {
    "http": None,
    "https": None
}

def send_to_database(data):
    url = "https://bazarpulse.ir/receiver_longtoshort.php"

    try:
        response = requests.post(
            url,
            json=data,
            timeout=10,
            proxies=PROXIES_OFF
        )
        print("DB Response:", response.text)
        return response.text
    except Exception as e:
        print("DB ERROR:", str(e))
        return None


def safe_get(url):
    """درخواست امن با header برای جلوگیری از بلاک شدن"""
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    return requests.get(url, headers=headers, timeout=8, proxies=PROXIES_OFF)


def get_market_long_short_ratio():
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]

    weighted_ratio = 0.0
    total_volume = 0.0

    volume_data = {}
    ratio_data = {}

    for symbol in symbols:
        try:
            # حجم بازار اسپات
            url_stats = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            vol = float(safe_get(url_stats).json()["quoteVolume"])

            # نسبت لانگ/شورت فیوچرز
            url_ratio = f"https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol={symbol}&period=1h"
            ratio = float(safe_get(url_ratio).json()[0]["longShortRatio"])

            volume_data[symbol] = vol
            ratio_data[symbol] = ratio
            total_volume += vol

            print(f"{symbol} | vol={vol} | ratio={ratio}")

        except Exception as e:
            print(f"ERROR {symbol}: {e}")
            continue

    if total_volume == 0:
        result = {
            "status": "error",
            "message": "No data received"
        }
        print(result)
        return result

    for symbol in volume_data:
        weight = volume_data[symbol] / total_volume
        weighted_ratio += ratio_data[symbol] * weight

    final_ratio = round(weighted_ratio, 2)

    result = {
        "value": f"{final_ratio}:1",
        "sentiment": (
            "خریداران زیادند (احتمال ریزش)"
            if final_ratio > 1.2
            else "فروشندگان زیادند (احتمال رشد)"
            if final_ratio < 0.8
            else "بازار متعادل"
        ),
        "status": "success"
    }

    print("FINAL RESULT:", json.dumps(result, ensure_ascii=False, indent=2))

    send_to_database(result)
    return result


if __name__ == "__main__":
    get_market_long_short_ratio()
