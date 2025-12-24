import os
import requests
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def search_products(query: str):
    if not SERPAPI_KEY:
        raise RuntimeError("SERPAPI_KEY not found in .env")

    params = {
        "engine": "google_shopping",
        "q": query,
        "hl": "en",
        "gl": "in",
        "api_key": SERPAPI_KEY
    }

    response = requests.get(
        "https://serpapi.com/search",
        params=params,
        timeout=15
    )
    data = response.json()

    results = []

    for item in data.get("shopping_results", []):
        price_raw = item.get("price")
        if not price_raw:
            continue

        try:
            price = float(
                price_raw.replace("₹", "").replace(",", "")
            )
        except:
            continue

        link = (
            item.get("link")
            or item.get("product_link")
            or item.get("merchant_link")
        )

        if not link and item.get("title"):
            link = (
                "https://www.google.com/search?q="
                + urllib.parse.quote(item["title"])
            )

        results.append({
            "title": item.get("title"),
            "price": price,
            "source": item.get("source"),
            "link": link
        })

    return results
