import requests
import json

PROXIES_OFF = {
    "http": None,
    "https": None
}


def send_to_database(data):
    url = "https://bazarpulse.ir/receiver_longtoshort.php"

    try:
        r = requests.post(
            url,
            json=data,
            timeout=10,
            proxies=PROXIES_OFF
        )
        print("DB RESPONSE:", r.text)
        return r.text
    except Exception as e:
        print("DB ERROR:", e)
        return None


def safe_get(url):
    """request امن برای GitHub Actions"""
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        r = requests.get(url, headers=headers, timeout=8, proxies=PROXIES_OFF)
        return r.json()
    except Exception as e:
        print("REQUEST FAIL:", url, e)
        return None


def get_market_long_short_ratio():
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]

    volume_data = {}
    ratio_data = {}

    total_volume = 0.0
    weighted_ratio = 0.0

    for symbol in symbols:
        try:
            # ===== SPOT VOLUME =====
            url_stats = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            data_stats = safe_get(url_stats)

            if not data_stats or "quoteVolume" not in data_stats:
                print("BAD VOLUME RESPONSE:", symbol, data_stats)
                continue

            vol = float(data_stats["quoteVolume"])

            # ===== LONG/SHORT RATIO =====
            url_ratio = f"https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol={symbol}&period=1h"
            data_ratio = safe_get(url_ratio)

            if not data_ratio or not isinstance(data_ratio, list):
                print("BAD RATIO RESPONSE:", symbol, data_ratio)
                continue

            ratio = float(data_ratio[0].get("longShortRatio", 1))

            volume_data[symbol] = vol
            ratio_data[symbol] = ratio
            total_volume += vol

            print(f"{symbol} | VOL={vol} | RATIO={ratio}")

        except Exception as e:
            print("ERROR SYMBOL:", symbol, e)
            continue

    if total_volume == 0:
        result = {
            "status": "error",
            "message": "No valid data received"
        }
        print(result)
        return result

    # ===== weighted calculation =====
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
