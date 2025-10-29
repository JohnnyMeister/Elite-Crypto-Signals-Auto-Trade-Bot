# telegram_alert.py

import requests
import logging


def send_telegram_message(message: str, config: dict) -> None:
    telegram_token = config.get("telegram_token")
    telegram_chat_id = config.get("telegram_chat_id")

    if not telegram_token or not telegram_chat_id:
        logging.warning("Telegram not configured. Message not sent.")
        return

    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    data = {
        "chat_id": telegram_chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, data=data, timeout=15)
        if response.status_code != 200:
            logging.error(f"Failed to send Telegram message: {response.text}")
        else:
            logging.info("Message sent to Telegram.")
    except Exception as e:
        logging.error(f"Error sending Telegram message: {e}")
