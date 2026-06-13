import json
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

# متغیر نمونه که باید با HTML کامل شما جایگزین شود
html_content = """...""" 

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=5))
def extract_unlock_details(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # استخراج تاریخ
    date_val = "N/A"
    # پیدا کردن div حاوی "Estimated Date & Time"
    all_divs = soup.find_all('div', class_='flex flex-wrap gap-2')
    for div in all_divs:
        if "Estimated Date & Time" in div.text:
            date_val = div.find_all('div')[-1].text.strip()
            break
            
    data = {
        "estimated_date_time": date_val,
        "allocations": []
    }
    
    # استخراج جدول
    table_body = soup.find('tbody')
    if not table_body:
        raise ValueError("جدول Allocation پیدا نشد")
        
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 4:
            # استخراج نام تخصیص
            name_div = cols[0].find('div', class_='truncate')
            name = name_div.text.strip() if name_div else "Unknown"
            
            # استخراج مقدار ریلیز
            amount_div = cols[2]
            amount = amount_div.text.strip() if amount_div else "0"
            
            # استخراج درصد ریلیز
            pct_div = cols[3].find('div', class_='text-symmetric-success')
            pct = pct_div.text.strip() if pct_div else "0%"
            
            data["allocations"].append({
                "allocation_name": name,
                "release_amount": amount,
                "release_percentage": pct
            })
            
    return data

def save_to_json(data):
    with open("unlock_data.json", "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("اطلاعات با موفقیت در unlock_data.json ذخیره شد.")

try:
    result = extract_unlock_details(html_content)
    save_to_json(result)
except Exception as e:
    print(f"خطای جدی در پردازش: {e}")
    
