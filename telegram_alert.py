import requests

TELEGRAM_TOKEN = '8082678835:AAFswQELa4IcjKx1-yp4EyCInMrbx66Ri_s'
CHAT_ID = '5217154830'

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print("❌ Falha ao enviar alerta Telegram:", response.text)
        else:
            print("📨 Alerta Telegram enviado!")
    except Exception as e:
        print("❌ Erro no envio Telegram:", e)
