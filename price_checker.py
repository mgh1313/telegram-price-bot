import requests
from bs4 import BeautifulSoup

def fetch_prices():
    url = "https://persian-gamer.com/product-category/%d8%a7%da%a9%d8%a7%d9%86%d8%aa-%d9%82%d8%a7%d9%86%d9%88%d9%86%db%8c-%d9%be%d9%84%db%8c-%d8%a7%d8%b3%d8%aa%db%8c%d8%b4%d9%86/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    products = soup.select("ul.products li.product")
    results = []

    for p in products:
        title = p.select_one("h2.woocommerce-loop-product__title").text.strip()
        price = p.select_one("span.woocommerce-Price-amount").text.strip()
        results.append({
            "title": title,
            "price": price
        })
    
    return results
