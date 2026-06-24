import requests
import time
import json

# تنظیمات برای تلاش مجدد
MAX_RETRIES = 5
INITIAL_BACKOFF = 1  # ثانیه

def get_sentiment_by_ratio(ratio):
    """تحلیل وضعیت بازار بر اساس نسبت."""
    if ratio > 1.2:
        return "خریداران زیادند (احتمال ریزش)"
    elif ratio < 0.8:
        return "فروشندگان زیادند (احتمال رشد)"
    else:
        return "بازار متعادل"

def send_to_database(data):
    """ارسال داده‌ها به سرور با مدیریت خطا."""
    url = "https://bazarpulse.ir/receiver_longtoshort.php"
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.text
    except Exception as e:
        return f"خطا در ارسال به دیتابیس: {str(e)}"

def get_market_long_short_ratio():
    """دریافت و محاسبه نسبت لانگ/شورت با قابلیت Retry."""
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
    
    for attempt in range(MAX_RETRIES):
        try:
            weighted_ratio = 0.0
            total_volume = 0.0
            volume_data = {}
            ratio_data = {}

            for symbol in symbols:
                # دریافت حجم معاملات
                url_stats = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
                vol = float(requests.get(url_stats, timeout=5).json()['quoteVolume'])
                
                # دریافت نسبت لانگ/شورت
                url_ratio = f"https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol={symbol}&period=1h"
                ratio = float(requests.get(url_ratio, timeout=5).json()[0]['longShortRatio'])
                
                volume_data[symbol] = vol
                ratio_data[symbol] = ratio
                total_volume += vol

            if total_volume == 0:
                raise ValueError("حجم معاملات صفر است")
            
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
            
            # ارسال موفقیت‌آمیز به سرور
            send_to_database(result)
            return result

        except Exception as e:
            wait_time = INITIAL_BACKOFF * (2 ** attempt)
            print(f"تلاش {attempt + 1} با خطا مواجه شد: {e}. تلاش مجدد در {wait_time} ثانیه دیگر...")
            time.sleep(wait_time)
            
    return {"status": "error", "message": "تعداد تلاش‌ها به پایان رسید و اطلاعاتی دریافت نشد"}

if __name__ == "__main__":
    print(get_market_long_short_ratio())
