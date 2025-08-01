# trader.py
import time
import hmac
import hashlib
import requests
import json
import base64
from urllib.parse import urlencode

with open("config.json") as f:
    config = json.load(f)

API_KEY = config["coinbase_api_key"]
API_SECRET = config["coinbase_api_secret"].encode()
API_PASSPHRASE = config.get("coinbase_passphrase", "")
BASE_URL = "https://api.exchange.coinbase.com"

TRADE_AMOUNT = float(config.get("trade_amount", 10.0))  # USDC por trade
FAKE_MODE = config.get("mode") == "true"

def get_timestamp():
    return str(time.time())

def get_signature(timestamp, method, request_path, body):
    message = f"{timestamp}{method}{request_path}{body}"
    hmac_key = base64.b64decode(API_SECRET)
    signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
    return base64.b64encode(signature.digest()).decode()

def make_request(method, path, body=""):
    timestamp = get_timestamp()
    signature = get_signature(timestamp, method.upper(), path, body)

    headers = {
        "CB-ACCESS-KEY": API_KEY,
        "CB-ACCESS-SIGN": signature,
        "CB-ACCESS-TIMESTAMP": timestamp,
        "CB-ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json"
    }

    url = BASE_URL + path

    if method.upper() == "GET":
        response = requests.get(url, headers=headers)
    else:
        response = requests.post(url, headers=headers, data=body)

    if not response.ok:
        print(f"❌ Erro na requisição: {response.status_code} {response.text}")
    return response.json()

def place_order(symbol: str, price: float):
    base, quote = symbol.split("/")
    coinbase_symbol = f"{base}-{quote}"  # Ex: BTC-USDC

    body_dict = {
        "type": "limit",
        "side": "buy",
        "product_id": coinbase_symbol,
        "price": str(price),
        "size": str(TRADE_AMOUNT / price),  # quantidade a comprar
        "post_only": True
    }

    body = json.dumps(body_dict)
    path = "/orders"

    print(f"🚀 {'[FAKE]' if FAKE_MODE else ''} Enviando ordem para {symbol}...")

    if FAKE_MODE:
        print(f"💡 Modo FAKE: Compra simulada de {TRADE_AMOUNT / price:.4f} {base} a {price} {quote}.")
        return

    response = make_request("POST", path, body)
    if response.get("id"):
        print(f"✅ Ordem enviada com sucesso! ID: {response['id']}")
    else:
        print("⚠️ Falha ao enviar ordem.")

def execute_trade(pair: str, price: float):
    try:
        place_order(pair, price)
    except Exception as e:
        print(f"⚠️ Erro ao executar trade: {e}")
