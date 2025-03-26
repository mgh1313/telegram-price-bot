from flask import Flask, send_from_directory
from telegram.ext import Updater, CommandHandler
import price_checker
import openpyxl
import os
import json

TOKEN = os.environ.get("BOT_TOKEN")
EXCEL_PATH = "static/data.xlsx"
JSON_PATH = "static/last_prices.json"

app = Flask(__name__)

@app.route("/")
def index():
    return "ربات تلگرام فعال است."

@app.route("/excel")
def download_excel():
    return send_from_directory("static", "data.xlsx", as_attachment=True)

def load_last_prices():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r") as f:
            return json.load(f)
    return {}

def save_last_prices(prices_dict):
    with open(JSON_PATH, "w") as f:
        json.dump(prices_dict, f)

def start(update, context):
    update.message.reply_text("سلام! برای بررسی قیمت‌ها دستور /check رو بزن.")

def check(update, context):
    prices = price_checker.fetch_prices()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["نام محصول", "قیمت"])

    new_prices = {}
    messages = []

    last_prices = load_last_prices()

    for item in prices:
        title = item['title']
        price = item['price']
        new_prices[title] = price
        ws.append([title, price])

        if title in last_prices and last_prices[title] != price:
            messages.append(f"🔄 تغییر قیمت: {title}\nقدیم: {last_prices[title]}\nجدید: {price}")

    wb.save(EXCEL_PATH)
    save_last_prices(new_prices)

    if messages:
        for msg in messages:
            update.message.reply_text(msg)

    update.message.reply_text("✅ قیمت‌ها دریافت شد.\n📥 لینک اکسل:\nhttps://<your-render-domain>/excel")

def run_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("check", check))
    updater.start_polling()

if __name__ == "__main__":
    run_bot()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
