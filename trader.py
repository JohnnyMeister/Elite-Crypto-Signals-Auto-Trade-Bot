# trader.py

import logging
import json
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException
from telegram_alert import send_telegram_message  # adiciona alertas telegram

logging.basicConfig(level=logging.INFO)

# Carregamento config
with open("config.json") as f:
    cfg = json.load(f)

API_KEY = cfg["binance_api_key"]
API_SECRET = cfg["binance_api_secret"]
FIXED_AMOUNT = float(cfg.get("fixed_amount", 10.0))
TEST_MODE = cfg.get("test_mode", True)

client = None
if not TEST_MODE:
    client = Client(API_KEY, API_SECRET)

def symbol_exists(symbol: str) -> bool:
    try:
        exchange_info = client.get_exchange_info()
        symbols = [s["symbol"] for s in exchange_info["symbols"]]
        return symbol.upper() in symbols
    except Exception as e:
        logging.error(f"Erro ao verificar símbolo: {e}")
        return False

def execute_trade(pair: str, entry_price: float, targets: list = None, stop_loss: float = None):
    symbol = pair.replace("/", "").upper()
    logging.info(f"💱 Iniciando trade: {symbol} a {entry_price}, valor {FIXED_AMOUNT} quote")

    if TEST_MODE:
        msg = f"[FAKE] Simulando entrada: {symbol} a {entry_price} com {FIXED_AMOUNT} USDT\nTP={targets}\nSL={stop_loss}"
        logging.info(msg)
        send_telegram_message(msg, cfg)
        return msg

    if not symbol_exists(symbol):
        msg = f"❌ Símbolo não encontrado na Binance: {symbol}"
        logging.error(msg)
        send_telegram_message(msg, cfg)
        return msg

    try:
        avg_price = float(client.get_symbol_ticker(symbol=symbol)["price"])
        quantity = round(FIXED_AMOUNT / avg_price, 6)
        logging.info(f"Quantia calculada: {quantity} {symbol}")

        buy_order = client.order_market_buy(symbol=symbol, quoteOrderQty=FIXED_AMOUNT)
        logging.info(f"✅ Ordem de compra executada: {buy_order}")

        send_telegram_message(
            f"✅ COMPRA EXECUTADA:\nPar: {symbol}\nPreço atual: {avg_price}\nQtd: {quantity}\nTP: {targets[0] if targets else 'n/a'}\nSL: {stop_loss}",
            cfg
        )

        if targets and stop_loss:
            tp = targets[0]
            sl = stop_loss
            logging.info(f"🚩 Criando OCO SELL TP={tp}, SL={sl}")

            oco = client.create_oco_order(
                symbol=symbol,
                side="SELL",
                quantity=quantity,
                price=str(tp),
                stopPrice=str(sl),
                stopLimitPrice=str(sl),
                stopLimitTimeInForce="GTC"
            )
            logging.info(f"✅ OCO Sell criada: {oco}")

            send_telegram_message(
                f"📍 OCO criada com sucesso\nTP: {tp}\nSL: {sl}",
                cfg
            )
            return f"[REAL] Buy ID:{buy_order['orderId']}, OCO Created"

        return f"[REAL] Buy feito ID:{buy_order['orderId']}"

    except BinanceAPIException as e:
        error_msg = f"❌ Binance API ERROR: {str(e)}"
        logging.error(error_msg)
        send_telegram_message(error_msg, cfg)
        return error_msg

    except Exception as e:
        error_msg = f"❌ ERRO GERAL: {str(e)}"
        logging.error(error_msg)
        send_telegram_message(error_msg, cfg)
        return error_msg
