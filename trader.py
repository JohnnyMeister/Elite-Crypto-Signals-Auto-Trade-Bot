# trader.py
import logging
import random
import time

try:
    from coinbase.wallet.client import Client as CoinbaseClient
except ImportError:
    CoinbaseClient = None  # Coinbase SDK não instalado

logging.basicConfig(level=logging.INFO)

with open("config.json") as f:
    import json
    config = json.load(f)

API_KEY = config.get("coinbase_api_key")
API_SECRET = config.get("coinbase_api_secret")
FIXED_AMOUNT = float(config.get("fixed_amount", 10.0))
TEST_MODE = config.get("test_mode", True)


# Inicializa cliente real se disponível e em modo real
coinbase = None
if not TEST_MODE and CoinbaseClient and API_KEY and API_SECRET:
    try:
        coinbase = CoinbaseClient(API_KEY, API_SECRET)
        logging.info("🔗 Cliente Coinbase inicializado.")
    except Exception as e:
        logging.error(f"❌ Erro ao inicializar cliente Coinbase: {e}")


def execute_trade(pair: str, entry_price: float, targets=None, stop_loss=None):
    if TEST_MODE or not coinbase:
        return simulate_trade(pair, entry_price, targets, stop_loss)
    else:
        return place_real_trade(pair, entry_price, targets, stop_loss)


def simulate_trade(pair, entry, targets, stop):
    logging.info(f"[FAKE TRADE] 💹 Simulando trade para {pair} a {entry}")
    logging.info(f"🎯 TP: {targets}, 🛑 SL: {stop}, 💵 Valor: {FIXED_AMOUNT} USDC")
    # Simula delay de execução e resultado aleatório
    time.sleep(1)
    simulated_result = random.choice(["Simulado com sucesso", "Falha na simulação"])
    return simulated_result


def place_real_trade(pair, entry, targets, stop):
    logging.info(f"[REAL TRADE] 📈 Executando trade real: {pair} a {entry}")

    try:
        # Extrai símbolo base (ex: ADA) e moeda cotada (ex: USDC)
        base_currency, quote_currency = pair.upper().split("/")
        account = coinbase.get_account(quote_currency)
        available_balance = float(account['balance']['amount'])

        if available_balance < FIXED_AMOUNT:
            raise ValueError(f"Saldo insuficiente. Disponível: {available_balance} {quote_currency}")

        # Compra de valor fixo (market order simulada)
        buy = coinbase.buy(
            account['id'],
            amount=str(FIXED_AMOUNT),
            currency=base_currency,
            payment_method=None,
            commit=True
        )

        logging.info(f"✅ Compra realizada: {buy}")

        # Stop-loss e take-profit são operacionais apenas via webhook ou trading bot externo
        logging.warning("⚠️ Coinbase API não suporta TP/SL nativamente. Use monitoramento externo.")

        return f"Compra real feita para {pair} a {entry}. TP/SL devem ser geridos manualmente."

    except Exception as e:
        logging.error(f"❌ Erro ao executar trade real: {e}")
        raise