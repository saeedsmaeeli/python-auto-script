import requests
import json

def get_sentiment_by_ratio(ratio):
    if ratio > 1.2: return "خریداران زیادند (احتمال ریزش)"
    elif ratio < 0.8: return "فروشندگان زیادند (احتمال رشد)"
    else: return "بازار متعادل"

def send_to_database(data):
    url = "https://bazarpulse.ir/receiver_longtoshort.php"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.post(url, json=data, headers=headers, timeout=15)
        return response.text
    except Exception as e:
        return str(e)

def get_market_long_short_ratio():
    # تنظیمات پراکسی برای دور زدن محدودیت IP
    # استفاده از سرویس پراکسی عمومی (Free Proxy)
    proxies = {
        'http': 'http://167.172.248.86:80',
        'https': 'http://167.172.248.86:80',
    }
    
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
    weighted_ratio = 0.0
    total_volume = 0.0
    volume_data = {}
    ratio_data = {}

    for symbol in symbols:
        try:
            # ارسال درخواست با تنظیمات پراکسی
            url_stats = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            vol = float(requests.get(url_stats, proxies=proxies, timeout=10).json()['quoteVolume'])
            
            url_ratio = f"https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol={symbol}&period=1h"
            ratio = float(requests.get(url_ratio, proxies=proxies, timeout=10).json()[0]['longShortRatio'])
            
            volume_data[symbol] = vol
            ratio_data[symbol] = ratio
            total_volume += vol
        except Exception as e:
            print(f"خطا در دریافت دیتا برای {symbol}: {e}")
            continue

    if total_volume == 0:
        return {"status": "error", "message": "اطلاعاتی دریافت نشد"}
    
    for symbol in symbols:
        if symbol in volume_data:
            weight = volume_data[symbol] / total_volume
            weighted_ratio += ratio_data[symbol] * weight
            
    final_ratio = round(weighted_ratio, 2)
    result = {
        "value": f"{final_ratio}:1",
        "sentiment": get_sentiment_by_ratio(final_ratio),
        "status": "success"
    }
    
    send_to_database(result)
    return result

if __name__ == "__main__":
    print(get_market_long_short_ratio())
