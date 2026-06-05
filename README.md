# BestPrice Scraper 🛒

## Kya Karta Hai?
Blinkit, Zepto, Swiggy Instamart se real-time prices compare karta hai!

## Files:
- `scraper.py` — Main server + scraper code
- `requirements.txt` — Python libraries
- `Procfile` — Railway ke liye

## Railway Pe Deploy Kaise Karein:
1. Yeh repository Railway se connect karo
2. Railway automatically deploy kar dega
3. URL milega jaise: `https://bestprice-xyz.railway.app`
4. Us URL ko BestPrice app mein lagao

## API Use Karna:
- Health check: `GET /`
- Search: `GET /search/pepsi`
- Popular: `GET /popular`
