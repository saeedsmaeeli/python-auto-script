import ccxt
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
        return response.status_code == 200
    except:
        return False

def get_market_long_short_ratio():
    # استفاده از CCXT برای اتصال پایدار
    exchange = ccxt.binance({'options': {'defaultType': 'future'}})
    symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"]
    
    # آدرس API بایننس که گاهی از طریق پروکسی‌های عمومی در دسترس است
    # اگر همچنان بلاک بود، از این URL جایگزین استفاده میکنیم:
    base_url = "https://fapi.binance.com/futures/data/globalLongShortAccountRatio"
    
    ratio_data = {}
    volume_data = {}
    total_volume = 0
    
    for symbol in symbols:
        try:
            # دریافت حجم معاملات (استفاده از ticker)
            ticker = exchange.fetch_ticker(symbol)
            vol = ticker['quoteVolume']
            
            # دریافت نسبت لانگ/شورت
            params = {'symbol': symbol.replace('/', ''), 'period': '1h'}
            response = requests.get(base_url, params=params, timeout=10)
            ratio = float(response.json()[0]['longShortRatio'])
            
            ratio_data[symbol] = ratio
            volume_data[symbol] = vol
            total_volume += vol
        except Exception as e:
            print(f"خطا برای {symbol}: {e}")
            continue

    if total_volume == 0: return None
    
    weighted_ratio = sum((ratio_data[s] * volume_data[s]) for s in symbols if s in ratio_data) / total_volume
    final_ratio = round(weighted_ratio, 2)
    
    result = {
        "value": f"{final_ratio}:1",
        "sentiment": get_sentiment_by_ratio(final_ratio)
    }
    
    send_to_database(result)
    return result

if __name__ == "__main__":
    # نصب کتابخانه ccxt در ورک‌فلو یادتان نرود!
    get_market_long_short_ratio()
