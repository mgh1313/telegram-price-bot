
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from flask import Flask, send_file, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

app = Flask(__name__)

PRODUCTS = []
EXCEL_PATH = "static/products.xlsx"
BOT_TOKEN = os.environ.get("BOT_TOKEN")

def scrape_products():
    global PRODUCTS
    PRODUCTS = []
    page = 1
    while True:
        url = f"https://persian-gamer.com/product-category/psn-game-account/page/{page}/"
        response = requests.get(url)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select("ul.products li.product")
        if not items:
            break

        for item in items:
            title_tag = item.select_one(".woocommerce-loop-product__title")
            price_tag = item.select_one(".price")
            if title_tag and price_tag:
                title = title_tag.text.strip()
                price = price_tag.text.strip()

                capacity = ""
                platform = ""
                if "ظرفیت" in title:
                    parts = title.split("ظرفیت")
                    name = parts[0].strip()
                    rest = parts[1].strip().split(" ", 1)
                    capacity = rest[0]
                    platform = rest[1] if len(rest) > 1 else ""
                else:
                    name = title

                PRODUCTS.append({
                    "نام محصول": name,
                    "ظرفیت": capacity,
                    "پلتفرم": platform,
                    "قیمت": price
                })
        page += 1

    save_to_excel()

def save_to_excel():
    df = pd.DataFrame(PRODUCTS)
    df.to_excel(EXCEL_PATH, index=False)

@app.route("/excel")
def download_excel():
    return send_file(EXCEL_PATH, as_attachment=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! با دستور /check فایل اکسل قیمت‌ها رو بگیر یا اسم محصولی رو تایپ کن مثل fc 25 تا قیمت‌هاشو ببینی.")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = request.host_url + "excel"
    await update.message.reply_text(f"✅ قیمت‌ها دریافت شد.\n📥 لینک اکسل:\n{https://telegram-price-bot-1.onrender.com/excel}")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower()
    results = [p for p in PRODUCTS if query in p['نام محصول'].lower()]
    if not results:
        await update.message.reply_text("❌ چیزی پیدا نشد.")
        return

    messages = []
    for r in results:
        messages.append(f"📌 {r['نام محصول']}\n📦 ظرفیت: {r['ظرفیت']} - 🎮 {r['پلتفرم']}\n💵 قیمت: {r['قیمت']}")

    for msg in messages:
        await update.message.reply_text(msg)

def run_telegram_bot():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("check", check))
    app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search))
    app_bot.run_polling()

if __name__ == '__main__':
    if not os.path.exists("static"):
        os.makedirs("static")
    scrape_products()
    run_telegram_bot()
    app.run(debug=False, port=5000)
