import requests
import json
import time

def get_sentiment_by_ratio(ratio):
    if ratio > 1.2: return "خریداران زیادند (احتمال ریزش)"
    elif ratio < 0.8: return "فروشندگان زیادند (احتمال رشد)"
    else: return "بازار متعادل"

def send_to_database(data):
    url = "https://bazarpulse.ir/receiver_longtoshort.php"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.post(url, json=data, headers=headers, timeout=20)
        return response.text
    except Exception as e:
        return str(e)

def get_market_long_short_ratio():
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
    results_list = []
    
    # استفاده از یک Session برای ثابت ماندن هدرها
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
    
    for symbol in symbols:
        time.sleep(3) 
        try:
            url_stats = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            response_stats = session.get(url_stats, timeout=15)
            
            url_ratio = f"https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol={symbol}&period=1h"
            response_ratio = session.get(url_ratio, timeout=15)
            
            if response_stats.status_code == 200 and response_ratio.status_code == 200:
                vol = float(response_stats.json()['quoteVolume'])
                ratio = float(response_ratio.json()[0]['longShortRatio'])
                results_list.append({"symbol": symbol, "vol": vol, "ratio": ratio})
            else:
                print(f"Error {symbol}: Stats={response_stats.status_code}, Ratio={response_ratio.status_code}")
                # چاپ متن خطا در صورت بلاک شدن
                if response_stats.status_code == 403:
                    print("هشدار: دسترسی توسط بایننس مسدود شده است (403 Forbidden).")
        except Exception as e:
            print(f"Exception for {symbol}: {e}")

    if not results_list:
        return {"status": "error", "message": "اطلاعاتی از API دریافت نشد"}
    
    total_volume = sum(item['vol'] for item in results_list)
    weighted_ratio = sum((item['ratio'] * item['vol']) for item in results_list) / total_volume
    
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
