import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time
import os

BASE_URL = "https://www.yahoo.com"
NEWS_URL = "https://www.yahoo.com/news/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

session = requests.Session()
session.headers.update(headers)

# ---------------- ARTICLE TEXT ----------------
def extract_article_paragraphs(soup, max_paragraphs=8):
    selectors = [
        'div[data-article-body="true"]',
        'article',
        'main article'
    ]

    container = None
    for sel in selectors:
        container = soup.select_one(sel)
        if container:
            break

    if not container:
        return []

    paragraphs = []
    for p in container.find_all("p"):
        text = p.get_text(" ", strip=True)
        if len(text) < 20:
            continue
        paragraphs.append(text)
        if len(paragraphs) >= max_paragraphs:
            break

    return paragraphs


def fetch_article_text(url):
    for attempt in range(10):
        try:
            r = session.get(url, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            paragraphs = extract_article_paragraphs(soup)
            return " ".join(paragraphs)
        except:
            time.sleep(1)

    return ""


# ---------------- SCRAPE YAHOO ----------------
def scrape_yahoo_first_15():
    news = []

    for attempt in range(10):
        try:
            r = session.get(NEWS_URL, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")

            news_list = soup.find("ul", class_="flex flex-col gap-4 sm:gap-6")
            if not news_list:
                time.sleep(1)
                continue

            items = news_list.find_all("li", class_="list-none")[:8]

            for item in items:
                title_tag = item.find("h3")
                a_tag = title_tag.find("a") if title_tag else None
                if not a_tag:
                    continue

                title = a_tag.get_text(strip=True)
                link = urljoin(BASE_URL, a_tag["href"])

                article_text = fetch_article_text(link)

                news.append({
                    "title": title,
                    "text": article_text
                })

                time.sleep(1)

            if news:
                return news

        except:
            time.sleep(1)

    return news


# ---------------- GPT ANALYSIS ----------------
def build_prompt(news):
       prompt = """
You are a CRYPTO MACRO IMPACT CLASSIFIER.
Your task is to evaluate each news item and determine its likely impact on Bitcoin and the broader cryptocurrency market.
Think ONLY through these 10 drivers:
Interest Rates
Global Liquidity
Inflation Expectations
USD Strength
Bond Yields
Risk-On / Risk-Off Sentiment
Recession / Credit Conditions
Crypto Regulation
Institutional Capital Flows
Geopolitical Risk
SCORING
1 = Positive for crypto 0 = Neutral / No meaningful crypto impact -1 = Negative for crypto
POSITIVE (+1)
Assign +1 when the news is likely to:
Increase global liquidity
Increase expectations of interest-rate cuts
Increase expectations of easier monetary policy
Weaken the US Dollar
Lower bond yields
Improve risk appetite
Boost stock markets broadly
Increase institutional investment into crypto
Support crypto adoption or regulation
Introduce monetary stimulus, QE, or liquidity injections
Examples:
Fed signals rate cuts
Inflation falls significantly
Central bank announces QE
Major crypto ETF approval
Large institutional crypto purchases
Significant weakening of the USD
Strong risk-on market environment
NEGATIVE (-1)
Assign -1 when the news is likely to:
Reduce liquidity
Increase expectations of rate hikes
Strengthen the US Dollar
Increase bond yields
Create risk-off sentiment
Increase recession fears
Tighten credit conditions
Restrict crypto usage or adoption
Increase geopolitical risk that causes market fear
Examples:
Hawkish central bank statements
Interest-rate hikes
Quantitative tightening (QT)
Strong USD rally
Stock market selloff
Crypto bans or severe restrictions
Banking stress without liquidity support
War escalation causing global market anxiety
Major disruptions to energy supply or trade routes
NEUTRAL (0)
Assign 0 when the news cannot be clearly linked to any of the 10 drivers above.
Examples:
Elections without economic consequences
Political speeches
Diplomatic meetings
Government reshuffles
Local political disputes
Natural disasters with limited global economic impact
Crime reports
Sports news
Entertainment news
Corporate news unrelated to liquidity, regulation, risk sentiment, or capital flows
International visits and summits without market implications
IMPORTANT RULES
Think like a macro trader, not a journalist.
Focus on capital flows, liquidity, and risk sentiment.
Ignore emotional or sensational language.
If the connection to crypto is weak or unclear, return 0.
News does NOT need to mention Bitcoin or crypto explicitly.
Evaluate indirect effects through the 10 drivers.
Do not guess hidden impacts that are not supported by the text.
Most news should be 0.
OUTPUT FORMAT
Return ONLY one number per news item.
Valid outputs:
1 0 -1
No explanations. No bullet points. No extra text. Only the scores in the same order as the input news items.
"""

    for i, n in enumerate(news):
        prompt += f"\n{i+1}. {n['title']}\n{n['text'][:800]}\n"

    return prompt


# ---------------- API CALL (WITH RETRY) ----------------
def call_model(prompt):

    url = "https://openrouter.ai/api/v1/chat/completions"
    API_KEY = os.getenv("API_KEY_DEEPSEEK")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek/deepseek-v4-flash",
        "temperature": 0.05,
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    for attempt in range(10):
        try:
            r = requests.post(
                url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )

            data = r.json()

            return data["choices"][0]["message"]["content"]

        except:
            time.sleep(2)

    return ""


# ---------------- MAIN ----------------
news = scrape_yahoo_first_15()
prompt = build_prompt(news)

scores_text = call_model(prompt)

scores = []
for line in scores_text.splitlines():
    line = line.strip()
    if line in ["-1", "0", "1"]:
        scores.append(int(line))

# ---------------- MERGE ----------------
results = []
for i, article in enumerate(news):
    score = scores[i] if i < len(scores) else 0
    results.append({
        "title": article["title"],
        "score": score
    })


# ---------------- SAVE ----------------
with open("crypto_news_sentiment.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("✅ saved crypto_news_sentiment.json")



























 
