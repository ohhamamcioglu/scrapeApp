import requests
import json

def debug_debenhams():
    APP_ID = "HNC30IYYNP"
    API_KEY = "6e5de83d201b6bdaac45d449a9466a42"
    INDEX_NAME = "debenhams-dbz-prod"
    url = f"https://{APP_ID}-dsn.algolia.net/1/indexes/{INDEX_NAME}/query"
    headers = {
        "X-Algolia-API-Key": API_KEY,
        "X-Algolia-Application-Id": APP_ID,
        "Content-Type": "application/json"
    }
    payload = {
        "query": "",
        "filters": "brand:Livabliss",
        "page": 0,
        "hitsPerPage": 1
    }
    
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    hits = data.get('hits', [])
    if hits:
        print(json.dumps(hits[0], indent=2))
    else:
        print("No hits found.")

if __name__ == "__main__":
    debug_debenhams()
