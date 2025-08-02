# trader.py

import logging
import json
import os
from binance.client import Client
from binance.exceptions import BinanceAPIException
from telegram_alert import send_telegram_message

logging.basicConfig(level=logging.INFO)

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError("❌ config.json não encontrado. Execute o main.py para criá-lo via GUI.")
    with open(CONFIG_FILE) as f:
        return json.load(f)

def get_binance_client(cfg, test_mode=False):
    if test_mode:
        return None
    return Client(cfg["binance_api_key"], cfg["binance_api_secret"])

def symbol_exists(symbol: str, client) -> bool:
    try:
        exchange_info = client.get_exchange_info()
        symbols = [s["symbol"] for s in exchange_info["symbols"]]
        return symbol.upper() in symbols
    except Exception as e:
        logging.error(f"Erro ao verificar símbolo: {e}")
        return False

def execute_trade(pair: str, entry_price: float, targets: list = None, stop_loss: float = None):
    cfg = load_config()
    test_mode = cfg.get("test_mode", True)
    fixed_amount = float(cfg.get("fixed_amount", 10.0))
    client = get_binance_client(cfg, test_mode)

    symbol = pair.replace("/", "").upper()
    logging.info(f"💱 Iniciando trade: {symbol} a {entry_price}, valor {fixed_amount} quote")

    if test_mode:
        msg = f"[FAKE] Simulando entrada: {symbol} a {entry_price} com {fixed_amount} USDT\nTP={targets}\nSL={stop_loss}"
        logging.info(msg)
        send_telegram_message(msg, cfg)
        return msg

    if not symbol_exists(symbol, client):
        msg = f"❌ Símbolo não encontrado na Binance: {symbol}"
        logging.error(msg)
        send_telegram_message(msg, cfg)
        return msg

    try:
        avg_price = float(client.get_symbol_ticker(symbol=symbol)["price"])
        quantity = round(fixed_amount / avg_price, 6)
        logging.info(f"Quantia calculada: {quantity} {symbol}")

        buy_order = client.order_market_buy(symbol=symbol, quoteOrderQty=fixed_amount)
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
