import logging
import threading
import time
import os
import requests
from flask import Flask

# Flask app to keep the service alive on free cloud hosts
app = Flask(__name__)


@app.route("/")
def home():
    return "Hot Wheels Tracker Bot is running!"


def run_bot():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
    )

    TELEGRAM_BOT_TOKEN = "8746211507:AAHI27hTvMGb0S8sOZoctwQqiO1HLlNc8zg" # Replace with your token
    CHAT_ID = "5262552780" # Replace with your chat ID
    PINCODE = "401303" # Your Virar PIN code

    # --- ADD ALL YOUR TARGET CARS HERE ---
    TRACKED_ITEMS = [
        {
            "url": "https://www.firstcry.com/product-url-slug-1",
            "name": "Nissan Skyline TH",
            "last_status": "Out of Stock",
        },
        {
            "url": " https://fclinks.firstcry.com/obZe/w9jq793w",
            "name": "REXY",
            "last_status": "Out of Stock",
        },
        {
            "url": "https://fclinks.firstcry.com/obZe/eg9eunki",
            "name": "STH",
            "last_status": "Out of Stock",
        },
        # Just copy, paste, and edit a new block for every car you want to add!
    ]

    def send_telegram_message(message):
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            logging.error(f"Telegram error: {e}")

    send_telegram_message(
        f"🤖 Cloud Hot Wheels Tracker Bot is live tracking {len(TRACKED_ITEMS)} cars!"
    )

    while True:
        for item in TRACKED_ITEMS:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            try:
                response = requests.get(
                    item["url"], headers=headers, timeout=15
                )
                if response.status_code == 200:
                    html = response.text.lower()
                    if (
                        "add to cart" in html
                        or "buy now" in html
                        or "in stock" in html
                    ):
                        current_status = "In Stock"
                    else:
                        current_status = "Out of Stock"
                else:
                    current_status = "Out of Stock"
            except Exception:
                current_status = "Out of Stock"

            logging.info(f"Checked {item['name']}: {current_status}")

            # If status flips, trigger alert and update status
            if (
                current_status == "In Stock"
                and item["last_status"] == "Out of Stock"
            ):
                alert_message = (
                    f"🚨 *HOT WHEELS BACK IN STOCK!* 🚨\n\n"
                    f"Car: {item['name']}\n"
                    f"PIN Code: {PINCODE}\n"
                    f"Link: {item['url']}"
                )
                send_telegram_message(alert_message)
                item["last_status"] = "In Stock"
            elif current_status == "Out of Stock":
                item["last_status"] = "Out of Stock"

            # Small delay between checking each link to avoid hammering the server
            time.sleep(3)

        # Wait 5 minutes before looping through the entire watchlist again
        time.sleep(300)


# Run the stock checker thread alongside the web server
if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)