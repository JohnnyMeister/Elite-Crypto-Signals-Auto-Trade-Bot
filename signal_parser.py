# signal_parser.py
import re
from trader import execute_trade

def parse_signal(message: str):
    """
    Extrai par de trading e preço de entrada de uma mensagem.
    Suporta múltiplas variações como:
    - "Buy around 0.08499"
    - "Entry around 0.7895"
    - "Buy @ 0.120"
    - "Entry: 0.675"
    """

    # Procurar par como BTC/USDT ou ADA/USDC
    pair_match = re.search(r"#?(\w{2,10})\s*/\s*(USDT|USDC)", message, re.IGNORECASE)
    if not pair_match:
        return False

    base, quote = pair_match.group(1).upper(), pair_match.group(2).upper()
    pair = f"{base}/{quote}"

    # Procurar entrada (diversas variações)
    price_patterns = [
        r"(?i)buy\s*(?:around|@|at)?\s*([0-9]*\.?[0-9]+)",
        r"(?i)entry\s*(?:around|@|at|:)?\s*([0-9]*\.?[0-9]+)"
    ]

    for pattern in price_patterns:
        price_match = re.search(pattern, message)
        if price_match:
            try:
                price = float(price_match.group(1))
                return {"pair": pair, "price": price}
            except ValueError:
                continue

    return False

