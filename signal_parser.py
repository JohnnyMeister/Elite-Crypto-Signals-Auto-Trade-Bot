# signal_parser.py

import re
import logging

logging.basicConfig(level=logging.INFO)

def parse_signal(message: str):
    """
    Extrai os dados de um sinal de trading em texto.
    Espera entradas como:
    #COIN/USDT
    Entry around 0.1234
    Targets: 0.125, 0.130, ...
    Stop around – 0.1150
    """

    try:
        # Extrair par
        pair_match = re.search(r"#?([A-Z]{2,10})\/(USDT|USDC)", message, re.IGNORECASE)
        if not pair_match:
            logging.warning("❌ Par de moedas não encontrado.")
            return False

        pair = f"{pair_match.group(1).upper()}/{pair_match.group(2).upper()}"

        # Entry
        entry_match = re.search(r"(Entry|Buy)\s+around\s+([\d.]+)", message, re.IGNORECASE)
        if not entry_match:
            logging.warning("❌ Preço de entrada não encontrado.")
            return False

        entry_price = float(entry_match.group(2))

        # Targets
        targets = re.findall(r"[\d.]+", re.search(r"(Targets|Target).*", message, re.IGNORECASE | re.DOTALL).group())
        targets = list(map(float, targets)) if targets else []

        # Stop
        stop_match = re.search(r"(Stop|SL).*?([\d.]+)", message, re.IGNORECASE)
        stop_loss = float(stop_match.group(2)) if stop_match else None

        if not targets or stop_loss is None:
            logging.warning("⚠️ Sinal incompleto (TP ou SL ausente).")
            return False

        result = {
            "pair": pair,
            "entry": entry_price,
            "targets": targets,
            "stop_loss": stop_loss
        }

        logging.info(f"📥 Sinal processado: {result}")
        return result

    except Exception as e:
        logging.error(f"Erro ao processar sinal: {e}")
        return False
