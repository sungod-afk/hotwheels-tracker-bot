import logging
import os
import threading
import time
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
  """Background loop that checks FirstCry stock every 5 minutes."""
  token = os.environ.get("8746211507:AAHI27hTvMGb0S8sOZoctwQqiO1HLlNc8zg")
  chat_id = os.environ.get("5262552780")

  # Define your 5 cars with a label and their FirstCry URL
  cars_to_track = {
      "Plymouth (STH)": "https://fclinks.firstcry.com/obZe/eg9eunki",
      "Nissan Skyline TH": "https://fclinks.firstcry.com/obZe/4o7zraxx",
      "REXY": "https://fclinks.firstcry.com/obZe/w9jq793w",
      "DINO": "https://fclinks.firstcry.com/obZe/087k0h1o",
      "RAM STH": "https://fclinks.firstcry.com/obZe/pwhzhqlt",
  }

  logging.info(f"Started Hot Wheels tracker monitoring {len(cars_to_track)} cars!")

  # Send startup notification to Telegram
  if token and chat_id:
    try:
      requests.post(
          f"https://api.telegram.org/bot{token}/sendMessage",
          json={
              "chat_id": chat_id,
              "text": (
                  f"🤖 Cloud Hot Wheels Tracker Bot is live tracking"
                  f" {len(cars_to_track)} cars!"
              ),
          },
          timeout=10,
      )
    except Exception as e:
      logging.error(f"Failed to send startup message: {e}")

  # Keep track of last known stock status to avoid duplicate spam alerts
  stock_status = {name: True for name in cars_to_track.keys()}

  while True:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
            " like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    for name, url in cars_to_track.items():
      try:
        response = requests.get(url, headers=headers, timeout=15)

        # Basic stock verification: Adjust 'Out of Stock' based on FirstCry's exact page text layout
        is_out_of_stock = "Out of Stock" in response.text

        if not is_out_of_stock and stock_status[name]:
          # Car came IN stock!
          logging.info(f"ALERT: {name} is IN STOCK!")
          if token and chat_id:
            requests.post(
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
          stock_status[name] = False  # Mark as in-stock to prevent alert spam

        elif is_out_of_stock:
          logging.info(f"Checked {name}: Out of Stock")
          stock_status[name] = True

      except Exception as e:
        logging.error(f"Error checking {name} ({url}): {e}")

      # Small pause between each car request to be gentle on FirstCry's servers
      time.sleep(5)

    # Wait 5 minutes (300 seconds) before running the next full check cycle
    time.sleep(300)


if __name__ == "__main__":
  # 1. Start tracking loop in a background thread
  bot_thread = threading.Thread(target=tracking_loop)
  bot_thread.daemon = True
  bot_thread.start()

  # 2. Run Flask web server on Render's required port
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
