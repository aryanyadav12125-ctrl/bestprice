"""
BestPrice Auto Updater — Real Browser Scraper
===============================================
undetected-chromedriver se real Chrome browser chalata hai.
Blinkit, Zepto, Swiggy Instamart, Amazon — sab real data.
GitHub Actions pe FREE mein har 12 ghante chalega.
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import random
import urllib.parse
from datetime import datetime, timezone

# =====================================================================
# CONFIGURATION
# =====================================================================

AMAZON_TAG_ID = "bestpriceap01-21"

PRODUCTS_TO_SCRAPE = [
    {"keyword": "Maggi 2 Minute Noodles 70g",    "emoji": "🍜", "cat": ["noodles", "all"]},
    {"keyword": "Amul Gold Full Cream Milk 500ml","emoji": "🥛", "cat": ["dairy",   "all"]},
    {"keyword": "Lays Classic Salted Chips 26g",  "emoji": "🥔", "cat": ["snacks",  "all"]},
    {"keyword": "Pepsi 500ml Bottle",             "emoji": "🥤", "cat": ["drinks",  "all"]},
    {"keyword": "Aashirvaad Chakki Atta 5kg",     "emoji": "🌾", "cat": ["atta",    "all"]},
    {"keyword": "Amul Butter 500g",               "emoji": "🧈", "cat": ["dairy",   "all"]},
    {"keyword": "Britannia Good Day Biscuits",    "emoji": "🍪", "cat": ["snacks",  "all"]},
    {"keyword": "Tropicana Orange Juice 1 ltr",   "emoji": "🍊", "cat": ["drinks",  "all"]},
    {"keyword": "Tata Salt 1kg",                  "emoji": "🧂", "cat": ["atta",    "all"]},
    {"keyword": "Surf Excel Easy Wash 1kg",       "emoji": "🧺", "cat": ["household","all"]},
]

# =====================================================================
# DRIVER SETUP — Real Chrome, undetected mode
# =====================================================================

def create_driver():
    """GitHub Actions ke liye optimized Chrome driver"""
    options = uc.ChromeOptions()

    # Headless — GitHub Actions mein screen nahi hoti
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Real Indian user ki tarah dikhao
    options.add_argument("--lang=en-IN")
    options.add_argument("--accept-lang=en-IN,en;q=0.9,hi;q=0.8")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Linux; Android 13; Pixel 7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.6367.82 Mobile Safari/537.36"
    )

    driver = uc.Chrome(options=options, use_subprocess=True)

    # JavaScript se webdriver flag hatao
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


def human_delay(min_s=3.0, max_s=7.0):
    """Random human-like delay"""
    t = random.uniform(min_s, max_s)
    print(f"    ⏳ {t:.1f}s wait...")
    time.sleep(t)


def human_scroll(driver):
    """Page pe slowly scroll karo — real user jaisa"""
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport     = driver.execute_script("return window.innerHeight")
    current      = 0
    while current < min(total_height, 2500):
        scroll_by = random.randint(200, 500)
        driver.execute_script(f"window.scrollBy(0, {scroll_by});")
        current += scroll_by
        time.sleep(random.uniform(0.3, 0.8))


# =====================================================================
# BLINKIT SCRAPER
# =====================================================================

def scrape_blinkit(driver, keyword):
    """Blinkit website se real prices scrape karo"""
    results = []
    try:
        query = urllib.parse.quote(keyword)
        url   = f"https://blinkit.com/s/?q={query}"
        print(f"    🟡 Blinkit: {url}")

        driver.get(url)
        human_delay(5, 9)
        human_scroll(driver)
        human_delay(2, 4)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Blinkit product cards
        cards = soup.find_all("div", {"class": lambda c: c and "Product__UpdatedPlpProductContainer" in c})
        if not cards:
            # Fallback selector
            cards = soup.find_all("div", attrs={"data-testid": "plp-product"})
        if not cards:
            cards = soup.select("div[class*='plp-product']")

        print(f"    Found {len(cards)} Blinkit cards")

        for card in cards[:3]:
            try:
                # Name
                name_el = card.find("div", {"class": lambda c: c and "Product__UpdatedTitle" in c})
                if not name_el:
                    name_el = card.find("div", attrs={"class": lambda c: c and "product-name" in str(c).lower()})
                name = name_el.get_text(strip=True) if name_el else keyword

                # Price
                price_el = card.find("div", {"class": lambda c: c and "Product__UpdatedPriceAndAtcContainer" in c})
                if not price_el:
                    price_el = card.find(attrs={"class": lambda c: c and "price" in str(c).lower()})
                price_text = price_el.get_text(strip=True) if price_el else ""
                price = extract_price(price_text)

                # Image
                img_el = card.find("img")
                img    = img_el["src"] if img_el and img_el.get("src") else ""

                if name and price > 0:
                    results.append({
                        "platform": "blinkit",
                        "name":     name[:80],
                        "price":    price,
                        "mrp":      price,
                        "unit":     "",
                        "image":    img,
                        "link":     url,
                        "delivery": "10 mins",
                    })
            except Exception as e:
                print(f"    Blinkit card parse error: {e}")
                continue

    except Exception as e:
        print(f"    ❌ Blinkit failed: {e}")

    return results


# =====================================================================
# ZEPTO SCRAPER
# =====================================================================

def scrape_zepto(driver, keyword):
    """Zepto website se real prices scrape karo"""
    results = []
    try:
        query = urllib.parse.quote(keyword)
        url   = f"https://www.zepto.com/search?query={query}"
        print(f"    🟣 Zepto: {url}")

        driver.get(url)
        human_delay(5, 10)
        human_scroll(driver)
        human_delay(2, 4)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Zepto product cards
        cards = soup.find_all("div", {"class": lambda c: c and "ProductCard" in str(c)})
        if not cards:
            cards = soup.select("div[data-testid='product-card']")
        if not cards:
            cards = soup.find_all("div", attrs={"class": lambda c: c and "product" in str(c).lower() and "card" in str(c).lower()})

        print(f"    Found {len(cards)} Zepto cards")

        for card in cards[:3]:
            try:
                name_el  = card.find(["h3", "h4", "p"], {"class": lambda c: c and ("name" in str(c).lower() or "title" in str(c).lower())})
                name     = name_el.get_text(strip=True) if name_el else keyword

                price_el = card.find(["span", "div", "p"], {"class": lambda c: c and "price" in str(c).lower()})
                price_text = price_el.get_text(strip=True) if price_el else ""
                price    = extract_price(price_text)

                img_el = card.find("img")
                img    = img_el.get("src", "") if img_el else ""

                if name and price > 0:
                    results.append({
                        "platform": "zepto",
                        "name":     name[:80],
                        "price":    price,
                        "mrp":      price,
                        "unit":     "",
                        "image":    img,
                        "link":     url,
                        "delivery": "10 mins",
                    })
            except Exception as e:
                print(f"    Zepto card parse error: {e}")
                continue

    except Exception as e:
        print(f"    ❌ Zepto failed: {e}")

    return results


# =====================================================================
# SWIGGY INSTAMART SCRAPER
# =====================================================================

def scrape_instamart(driver, keyword):
    """Swiggy Instamart website se real prices scrape karo"""
    results = []
    try:
        query = urllib.parse.quote(keyword)
        url   = f"https://www.swiggy.com/instamart/search?query={query}"
        print(f"    🟠 Instamart: {url}")

        driver.get(url)
        human_delay(6, 10)
        human_scroll(driver)
        human_delay(2, 4)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Instamart product cards
        cards = soup.find_all("div", {"class": lambda c: c and "ItemWidget" in str(c)})
        if not cards:
            cards = soup.find_all("div", {"class": lambda c: c and "instamart" in str(c).lower() and "item" in str(c).lower()})
        if not cards:
            cards = soup.select("div[data-testid='item-widget']")

        print(f"    Found {len(cards)} Instamart cards")

        for card in cards[:3]:
            try:
                name_el  = card.find(["div", "span"], {"class": lambda c: c and ("name" in str(c).lower() or "title" in str(c).lower())})
                name     = name_el.get_text(strip=True) if name_el else keyword

                price_el = card.find(["div", "span"], {"class": lambda c: c and "price" in str(c).lower()})
                price_text = price_el.get_text(strip=True) if price_el else ""
                price    = extract_price(price_text)

                img_el = card.find("img")
                img    = img_el.get("src", "") if img_el else ""

                if name and price > 0:
                    results.append({
                        "platform": "instamart",
                        "name":     name[:80],
                        "price":    price,
                        "mrp":      price,
                        "unit":     "",
                        "image":    img,
                        "link":     url,
                        "delivery": "15 mins",
                    })
            except Exception as e:
                print(f"    Instamart card parse error: {e}")
                continue

    except Exception as e:
        print(f"    ❌ Instamart failed: {e}")

    return results


# =====================================================================
# AMAZON SCRAPER
# =====================================================================

def build_affiliate_url(raw_url):
    """Amazon URL clean karke affiliate tag lagao"""
    if "amazon.in" in raw_url:
        base = raw_url.split("?")[0].split("#")[0]
        return f"{base}?tag={AMAZON_TAG_ID}"
    return raw_url


def scrape_amazon(driver, keyword):
    """Amazon India se real prices + affiliate links"""
    results = []
    try:
        query = urllib.parse.quote(keyword)
        url   = f"https://www.amazon.in/s?k={query}"
        print(f"    🟤 Amazon: {url}")

        driver.get(url)
        human_delay(5, 9)
        human_scroll(driver)
        human_delay(2, 3)

        soup  = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.find_all("div", {"data-component-type": "s-search-result"})

        print(f"    Found {len(items)} Amazon items")

        for item in items[:3]:
            try:
                # Name
                h2   = item.find("h2")
                name = h2.get_text(strip=True) if h2 else keyword

                # Price
                price_el   = item.find("span", {"class": "a-price-whole"})
                price_text = price_el.get_text(strip=True).replace(",", "") if price_el else "0"
                price      = float(price_text) if price_text.replace(".", "").isdigit() else 0.0

                # MRP (original price)
                mrp_el   = item.find("span", {"class": "a-text-price"})
                mrp_text = mrp_el.get_text(strip=True).replace("₹", "").replace(",", "") if mrp_el else str(price)
                try:
                    mrp = float(mrp_text)
                except ValueError:
                    mrp = price

                # Link
                a_tag   = item.find("a", {"class": "a-link-normal"})
                raw_url = "https://www.amazon.in" + a_tag["href"] if a_tag else url
                aff_url = build_affiliate_url(raw_url)

                # Image
                img_tag = item.find("img", {"class": "s-image"})
                img_src = img_tag["src"] if img_tag else ""

                if name and price > 0:
                    results.append({
                        "platform": "amazon",
                        "name":     name[:80],
                        "price":    price,
                        "mrp":      mrp if mrp >= price else price,
                        "unit":     "",
                        "image":    img_src,
                        "link":     aff_url,
                        "delivery": "1-2 days",
                    })
            except Exception as e:
                print(f"    Amazon item parse error: {e}")
                continue

    except Exception as e:
        print(f"    ❌ Amazon failed: {e}")

    return results


# =====================================================================
# PRICE EXTRACTOR — "₹49", "Rs. 49", "49.00" sab handle karta hai
# =====================================================================

def extract_price(text):
    """String se price number nikalo"""
    import re
    if not text:
        return 0.0
    # Remove ₹, Rs., commas, spaces
    cleaned = re.sub(r"[₹Rs.,\s]", "", text)
    # First number find karo
    match = re.search(r"\d+\.?\d*", cleaned)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return 0.0
    return 0.0


# =====================================================================
# FALLBACK — Jab scraping fail ho
# =====================================================================

PRICE_RANGES = {
    "maggi":      {"blinkit": (14, 18),   "instamart": (16, 20),   "zepto": (13, 17),   "amazon": (12, 16)},
    "amul":       {"blinkit": (52, 58),   "instamart": (54, 60),   "zepto": (50, 56),   "amazon": (48, 55)},
    "lays":       {"blinkit": (20, 25),   "instamart": (22, 28),   "zepto": (19, 24),   "amazon": (18, 23)},
    "pepsi":      {"blinkit": (38, 46),   "instamart": (40, 50),   "zepto": (36, 44),   "amazon": (35, 42)},
    "aashirvaad": {"blinkit": (315, 330), "instamart": (318, 335), "zepto": (312, 328), "amazon": (310, 325)},
    "britannia":  {"blinkit": (30, 38),   "instamart": (32, 40),   "zepto": (28, 36),   "amazon": (27, 35)},
    "tropicana":  {"blinkit": (105, 115), "instamart": (108, 118), "zepto": (99, 110),  "amazon": (95, 108)},
    "tata":       {"blinkit": (28, 34),   "instamart": (28, 34),   "zepto": (27, 32),   "amazon": (26, 31)},
    "surf":       {"blinkit": (185, 200), "instamart": (188, 205), "zepto": (182, 198), "amazon": (178, 195)},
    "butter":     {"blinkit": (248, 262), "instamart": (250, 265), "zepto": (245, 260), "amazon": (242, 258)},
    "default":    {"blinkit": (80, 150),  "instamart": (85, 155),  "zepto": (78, 148),  "amazon": (75, 145)},
}

def get_fallback_price(keyword, platform):
    kw = keyword.lower()
    for key, ranges in PRICE_RANGES.items():
        if key in kw:
            lo, hi = ranges.get(platform, (80, 150))
            return round(random.uniform(lo, hi), 0)
    lo, hi = PRICE_RANGES["default"].get(platform, (80, 150))
    return round(random.uniform(lo, hi), 0)

def generate_fallback(keyword):
    """Realistic fallback prices — clearly marked"""
    platforms = {
        "blinkit":   {"time": "10 mins", "link": f"https://blinkit.com/s/?q={urllib.parse.quote(keyword)}"},
        "instamart": {"time": "15 mins", "link": f"https://www.swiggy.com/instamart/search?query={urllib.parse.quote(keyword)}"},
        "zepto":     {"time": "10 mins", "link": f"https://www.zepto.com/search?query={urllib.parse.quote(keyword)}"},
        "amazon":    {"time": "1-2 days","link": f"https://www.amazon.in/s?k={urllib.parse.quote(keyword)}&tag={AMAZON_TAG_ID}"},
    }
    results = []
    for plat, info in platforms.items():
        price = get_fallback_price(keyword, plat)
        results.append({
            "platform":    plat,
            "name":        keyword,
            "price":       price,
            "mrp":         price,
            "unit":        "",
            "image":       "",
            "link":        info["link"],
            "delivery":    info["time"],
            "is_fallback": True,
        })
    return results


# =====================================================================
# COMPARE & BUILD OUTPUT
# =====================================================================

def compare_product(driver, product_config, product_id):
    keyword = product_config["keyword"]
    emoji   = product_config["emoji"]
    cats    = product_config["cat"]

    print(f"\n{'='*50}")
    print(f"[{product_id}] Scraping: {keyword}")
    print(f"{'='*50}")

    # Scrape all platforms
    blinkit_data   = scrape_blinkit(driver, keyword)
    human_delay(3, 6)

    zepto_data     = scrape_zepto(driver, keyword)
    human_delay(3, 6)

    instamart_data = scrape_instamart(driver, keyword)
    human_delay(3, 6)

    amazon_data    = scrape_amazon(driver, keyword)
    human_delay(3, 6)

    all_results = blinkit_data + zepto_data + instamart_data + amazon_data

    # Fallback jab koi data nahi mila
    if not all_results:
        print(f"    ⚠️  No live data — using fallback")
        all_results = generate_fallback(keyword)
    else:
        # Missing platforms ke liye fallback add karo
        found_platforms = {r["platform"] for r in all_results}
        all_platforms   = {"blinkit", "zepto", "instamart", "amazon"}
        missing         = all_platforms - found_platforms

        for plat in missing:
            print(f"    ⚠️  {plat} missing — adding fallback")
            price = get_fallback_price(keyword, plat)
            all_results.append({
                "platform":    plat,
                "name":        keyword,
                "price":       price,
                "mrp":         price,
                "unit":        "",
                "image":       "",
                "link":        f"https://blinkit.com/s/?q={urllib.parse.quote(keyword)}" if plat == "blinkit" else f"https://www.amazon.in/s?k={urllib.parse.quote(keyword)}&tag={AMAZON_TAG_ID}",
                "delivery":    "10 mins" if plat != "amazon" else "1-2 days",
                "is_fallback": True,
            })

    # Price ke hisaab se sort karo (sasta pehle)
    all_results.sort(key=lambda x: x.get("price", 9999))

    # Best display name
    live_names   = [r["name"] for r in all_results if not r.get("is_fallback")]
    display_name = live_names[0][:70] if live_names else keyword

    # Frontend ke liye prices array
    prices = []
    for r in all_results:
        prices.append({
            "p":     r["platform"],
            "price": r["price"],
            "orig":  r["mrp"] if r.get("mrp", 0) > r["price"] else None,
            "size":  r.get("unit", ""),
            "link":  r["link"],
            "time":  r["delivery"],
            "live":  not r.get("is_fallback", False),
        })

    live_count = sum(1 for p in prices if p["live"])
    print(f"    ✅ Done — {live_count}/4 platforms live, {4-live_count} fallback")

    return {
        "id":         product_id,
        "keyword":    keyword,
        "name":       display_name,
        "brand":      keyword.split()[0],
        "emoji":      emoji,
        "cat":        cats,
        "prices":     prices,
        "live_count": live_count,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


# =====================================================================
# MAIN
# =====================================================================

def main():
    print("=" * 55)
    print("  BestPrice Auto Updater — Real Browser Mode")
    print(f"  Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 55)

    driver = create_driver()
    print("✅ Chrome driver ready!\n")

    master_output = []
    failed_products = []

    try:
        for idx, product in enumerate(PRODUCTS_TO_SCRAPE, start=1):
            try:
                result = compare_product(driver, product, product_id=idx)
                master_output.append(result)

                # Products ke beech extra cooldown
                if idx < len(PRODUCTS_TO_SCRAPE):
                    cooldown = random.randint(8, 15)
                    print(f"\n  💤 {cooldown}s cooldown...")
                    time.sleep(cooldown)

            except Exception as e:
                print(f"\n  ❌ Product {idx} failed: {e}")
                failed_products.append(product["keyword"])
                # Fallback data use karo
                fallback_prices = generate_fallback(product["keyword"])
                master_output.append({
                    "id":         idx,
                    "keyword":    product["keyword"],
                    "name":       product["keyword"],
                    "brand":      product["keyword"].split()[0],
                    "emoji":      product["emoji"],
                    "cat":        product["cat"],
                    "prices":     [{
                        "p":     r["platform"],
                        "price": r["price"],
                        "orig":  None,
                        "size":  "",
                        "link":  r["link"],
                        "time":  r["delivery"],
                        "live":  False,
                    } for r in fallback_prices],
                    "live_count": 0,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                })

    finally:
        driver.quit()
        print("\n✅ Browser closed.")

    # Final JSON output
    output = {
        "generated_at":    datetime.now(timezone.utc).isoformat(),
        "total_products":  len(master_output),
        "failed_products": failed_products,
        "products":        master_output,
    }

    with open("grocery_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    live_total = sum(p.get("live_count", 0) for p in master_output)
    print(f"\n{'='*55}")
    print(f"✅ grocery_data.json updated!")
    print(f"   Products: {len(master_output)}")
    print(f"   Failed:   {len(failed_products)}")
    print(f"   Live data points: {live_total}")
    print(f"{'='*55}")


if __name__ == "__main__":
    main()
