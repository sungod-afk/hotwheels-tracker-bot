import logging
import os
import threading
import time
from curl_cffi import requests as c_requests
from flask import Flask
import requests

# Set up logging for Render dashboard
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)


@app.route("/")
def home():
  return "Hot Wheels Tracker Bot is active!"


def tracking_loop():
  token = os.environ.get("8746211507:AAHI27hTvMGb0S8sOZoctwQqiO1HLlNc8zg")
  chat_id = os.environ.get("5262552780")

  cars_to_track = {
      "Plymouth STH": "https://fclinks.firstcry.com/obZe/eg9eunki",
      "Nissan Skyline TH": "https://fclinks.firstcry.com/obZe/4o7zraxx",
      "REXY": "https://fclinks.firstcry.com/obZe/w9jq793w",
      "DINO": "https://fclinks.firstcry.com/obZe/087k0h1o",
      "RAM STH": "https://fclinks.firstcry.com/obZe/pwhzhqlt",
      "Feline": "https://fclinks.firstcry.com/obZe/8kqfjluq",
  }

  logging.info(f"Started tracker monitoring {len(cars_to_track)} cars!")
  stock_status = {name: False for name in cars_to_track.keys()}

  while True:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
            " like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.firstcry.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    cookies = {"pincode": "401303"}

    for name, url in cars_to_track.items():
      try:
        # Extract product ID or use the direct page with browser impersonation
        response = c_requests.get(
            url, impersonate="chrome", cookies=cookies, timeout=15
        )
        page_text = response.text.upper()

        # Look for stock JSON flags or cart button availability in the rendered response
        is_available = (
            "ADD TO CART" in page_text
            or "BUYNOW" in page_text
            or '"STOCK":1' in page_text
            or '"IS_STOCK":TRUE' in page_text
        )
        is_explicitly_out = "OUT OF STOCK" in page_text or "SOLD OUT" in page_text

        if name == "Feline":
          logging.info(
              f"DEBUG Feline: Status {response.status_code} | Available flag:"
              f" {is_available} | Out flag: {is_explicitly_out}"
          )

        if (
            response.status_code == 200
            and is_available
            and not is_explicitly_out
        ):
          if not stock_status[name]:
            logging.info(f"REAL ALERT: {name} is confirmed IN STOCK!")
            if token and chat_id:
              tg_resp = requests.post(
                  f"https://api.telegram.org/bot{token}/sendMessage",
                  json={
                      "chat_id": chat_id,
                      "text": (
                          f"🔥 **{name}** is IN STOCK on FirstCry!\nGrab it"
                          f" now: {url}"
                      ),
                  },
                  timeout=10,
              )
              logging.info(f"Telegram response status: {tg_resp.status_code}")
            stock_status[name] = True
        else:
          logging.info(f"Checked {name}: Out of Stock")
          stock_status[name] = False

      except Exception as e:
        logging.error(f"Error checking {name}: {e}")

      time.sleep(5)

    time.sleep(120)

if __name__ == "__main__":
  # 1. Start tracking loop in a background thread
  bot_thread = threading.Thread(target=tracking_loop)
  bot_thread.daemon = True
  bot_thread.start()

  # 2. Run Flask web server on Render's required port
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)