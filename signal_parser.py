# signal_parser.py
import re
from trader import execute_trade

def parse_signal(message: str):
    pair_match = re.search(r"#(\w+)/(USDT|USDC)", message)
    price_match = re.search(r"(Buy|Entry) around (\d+(?:\.\d+)?)", message, re.IGNORECASE)

    if pair_match and price_match:
        symbol = pair_match.group(1)
        stable = pair_match.group(2)
        entry_price = float(price_match.group(2))

        pair = f"{symbol}/{stable}"
        print(f"📈 Sinal identificado: {pair} @ {entry_price}")

        execute_trade(pair, entry_price)
        return {
            "pair": pair,
            "entry_price": entry_price
        }

    print("⚠️ Nenhum sinal válido encontrado na mensagem.")
    return False
