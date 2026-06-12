import os
import requests
import json

token = os.getenv('API_TOKEN')
url = f'https://api.webz.io/newsApiLite?token={token}&q=Google%20topic:%22financial%20and%20economic%20news%22%20sentiment:negative'

response = requests.get(url)
with open('news_output.json', 'w', encoding='utf-8') as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=4)
