# backend/services/search.py
from dotenv import load_dotenv
import os
import serpapi

# --- Load environment variables ---
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
# print(f"[DEBUG] Loaded SERPAPI_KEY: {'SET' if SERPAPI_KEY else 'NOT SET'}", flush=True)

if not SERPAPI_KEY:
    raise ValueError("SERPAPI_KEY is missing in environment variables!")

def search_products(query: str, limit: int = 10):
    """
    Search products on Google Shopping using SerpApi.
    Returns a list of dicts with 'title', 'link', 'thumbnail', 'price'.
    """
    # print(f"[DEBUG] Starting product search for query: '{query}' with limit: {limit}", flush=True)
    try:
        params = {
            "q": query,
            "engine": "google",
            "tbm": "shop",
            "num": limit,
            "hl": "en",
            "gl": "us",
            "api_key": SERPAPI_KEY
        }
        # print(f"[DEBUG] Search params: {params}", flush=True)

        # Perform the search
        result = serpapi.search(params)
        # print(f"[DEBUG] Raw SerpApi result keys: {list(result.keys())}", flush=True)
        
        shopping_results = result.get("shopping_results", [])
        # print(f"[DEBUG] Number of shopping_results found: {len(shopping_results)}", flush=True)

        products = []
        for idx, item in enumerate(shopping_results, 1):
            title = item.get("title", "")
            price = item.get("price", "N/A")
            thumbnail = item.get("thumbnail") or "/static/img/placeholder.png"
            link = item.get("link") or item.get("product_link") or "#"

            # print(f"[DEBUG] Item {idx}: title={title}, price={price}, link={link}, thumbnail={thumbnail}", flush=True)

            products.append({
                "title": title,
                "link": link,
                "thumbnail": thumbnail,
                "price": price
            })


        # print(f"[DEBUG] Finished parsing products. Total: {len(products)}", flush=True)
        return products

    except Exception as e:
        print(f"[ERROR] SerpApi search failed: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return []

# --- Example usage ---
# if __name__ == "__main__":
#     query = "pink dress with bow neck"
#     results = search_products(query, limit=10)
#     print(f"[DEBUG] Final results length: {len(results)}", flush=True)
#     for idx, item in enumerate(results, 1):
#         print(f"{idx}. Title: {item['title']}")
#         print(f"   Price: {item['price']}")
#         print(f"   Link: {item['link']}")
#         print(f"   Thumbnail: {item['thumbnail']}\n")
