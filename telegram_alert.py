# telegram_alert.py

import requests
import logging

def send_telegram_message(message, config):
    telegram_token = config.get("telegram_token")
    telegram_chat_id = config.get("telegram_chat_id")

    if not telegram_token or not telegram_chat_id:
        logging.warning("🔕 Telegram não configurado. Mensagem não enviada.")
        return

    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    data = {
        "chat_id": telegram_chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            logging.error(f"❌ Falha ao enviar mensagem Telegram: {response.text}")
        else:
            logging.info("📨 Mensagem enviada para Telegram.")
    except Exception as e:
        logging.error(f"Erro ao enviar mensagem Telegram: {e}")
