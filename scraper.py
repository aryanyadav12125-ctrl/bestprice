import requests
import json
import time
import random
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# =====================
# HEADERS - Bot detection se bachne ke liye
# =====================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# =====================
# BLINKIT SCRAPER
# =====================
def get_blinkit_price(query):
    try:
        # Blinkit ka search API
        url = f"https://blinkit.com/v2/product/search"
        params = {
            "q": query,
            "start": 0,
            "size": 5,
            "lat": 28.6139,   # Delhi latitude
            "lon": 77.2090,   # Delhi longitude
        }
        headers = {**HEADERS, "app_client": "consumer_web"}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get("objects", [])
            
            results = []
            for item in products[:3]:
                product = item.get("data", {})
                results.append({
                    "name": product.get("name", ""),
                    "price": product.get("price", 0),
                    "mrp": product.get("mrp", 0),
                    "unit": product.get("unit", ""),
                    "image": product.get("image_url", ""),
                    "platform": "blinkit",
                    "delivery_time": "23 mins"
                })
            return results
        return []
    except Exception as e:
        print(f"Blinkit error: {e}")
        return []

# =====================
# ZEPTO SCRAPER
# =====================
def get_zepto_price(query):
    try:
        url = "https://api.zepto.com/api/v2/search"
        params = {
            "query": query,
            "pageNumber": 1,
            "pageSize": 5,
            "latitude": 28.6139,
            "longitude": 77.2090,
        }
        headers = {
            **HEADERS,
            "store_id": "delhi_store",
            "Referer": "https://www.zepto.com/",
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get("data", {}).get("products", [])
            
            results = []
            for item in products[:3]:
                results.append({
                    "name": item.get("name", ""),
                    "price": item.get("discountedPrice", item.get("price", 0)) / 100,
                    "mrp": item.get("mrp", 0) / 100,
                    "unit": item.get("unitSize", ""),
                    "image": item.get("imageUrl", ""),
                    "platform": "zepto",
                    "delivery_time": "15 mins"
                })
            return results
        return []
    except Exception as e:
        print(f"Zepto error: {e}")
        return []

# =====================
# SWIGGY INSTAMART SCRAPER
# =====================
def get_instamart_price(query):
    try:
        url = "https://www.swiggy.com/api/instamart/search"
        params = {
            "query": query,
            "lat": 28.6139,
            "lng": 77.2090,
        }
        headers = {
            **HEADERS,
            "Referer": "https://www.swiggy.com/instamart",
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get("data", {}).get("products", [])
            
            results = []
            for item in products[:3]:
                results.append({
                    "name": item.get("display_name", ""),
                    "price": item.get("price", {}).get("offer_price", 0) / 100,
                    "mrp": item.get("price", {}).get("mrp", 0) / 100,
                    "unit": item.get("weight", ""),
                    "image": item.get("image_id", ""),
                    "platform": "instamart",
                    "delivery_time": "26 mins"
                })
            return results
        return []
    except Exception as e:
        print(f"Instamart error: {e}")
        return []

# =====================
# COMBINE & COMPARE
# =====================
def compare_prices(query):
    # Thoda wait karo requests ke beech
    blinkit = get_blinkit_price(query)
    time.sleep(random.uniform(0.5, 1.5))
    
    zepto = get_zepto_price(query)
    time.sleep(random.uniform(0.5, 1.5))
    
    instamart = get_instamart_price(query)
    
    all_results = blinkit + zepto + instamart
    
    # Sort by price
    all_results.sort(key=lambda x: x.get("price", 999))
    
    return all_results

# =====================
# API ROUTES
# =====================

# Health check
@app.route("/")
def home():
    return jsonify({"status": "BestPrice Server Chal Raha Hai! ✅"})

# Search endpoint
@app.route("/search/<query>")
def search(query):
    try:
        results = compare_prices(query)
        return jsonify({
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Popular items ke liye
@app.route("/popular")
def popular():
    items = ["pepsi", "maggi", "amul milk", "lays chips", "britannia bread"]
    all_data = {}
    
    for item in items:
        all_data[item] = compare_prices(item)
        time.sleep(1)  # Rate limiting
    
    return jsonify({"success": True, "data": all_data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
