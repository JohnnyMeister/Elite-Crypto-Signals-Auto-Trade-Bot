# telegram_alert.py
import requests
import logging

def send_telegram_message(config, message):
    """
    Envia uma mensagem para o Telegram usando o bot e chat ID definidos na config.
    """
    try:
        token = config.get("telegram_token")
        chat_id = config.get("telegram_chat_id")

        if not token or not chat_id:
            logging.warning("⚠️ Telegram token ou chat_id não configurados.")
            return

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        response = requests.post(url, data=payload)
        response.raise_for_status()

        logging.info("📨 Mensagem enviada ao Telegram.")
    except Exception as e:
        logging.error(f"❌ Erro ao enviar mensagem Telegram: {str(e)}")
