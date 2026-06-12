import feedparser

rss_url = "RSS_URL_HERE"

feed = feedparser.parse(rss_url)

print("Feed title:", feed.feed.title)

for entry in feed.entries:
    print("-" * 50)
    print("Title:", entry.get("title", ""))
    print("Link:", entry.get("link", ""))
    print("Published:", entry.get("published", ""))
    print("Summary:", entry.get("summary", ""))
