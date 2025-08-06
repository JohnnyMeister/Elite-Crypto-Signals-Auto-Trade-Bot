# main.py
import asyncio
import platform

# ⚠️ Corrige problemas com aiodns no Windows
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import os
import json
from gui import show_gui
from Selfbot_listener import run_listener

CONFIG_FILE = "config.json"

def create_default_config():
    default_config = {
        "binance_api_key": "",
        "binance_api_secret": "",
        "telegram_token": "",
        "telegram_chat_id": "",
        "canal_id": "",
        "fixed_amount": 10.0,
        "test_mode": True
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(default_config, f, indent=4)
    print("✅ config.json criado. A abrir GUI para preencher os dados...")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        create_default_config()
        show_gui(True)
    with open(CONFIG_FILE) as f:
        return json.load(f)

def ask_test_mode():
    while True:
        resposta = input("❓ Desejas iniciar em modo de teste (fake trades)? (s/n): ").strip().lower()
        if resposta in ["s", "sim"]:
            return True
        elif resposta in ["n", "nao", "não"]:
            return False
        else:
            print("⚠️ Resposta inválida. Digita 's' ou 'n'.")

if __name__ == "__main__":
    config = load_config()

    print("\n📌 CONFIG CARREGADA:")
    for k, v in config.items():
        print(f"  - {k}: {v}")

    # Perguntar SEMPRE se quer modo de teste
    test_mode = ask_test_mode()
    config["test_mode"] = test_mode

    print(f"\n🚀 A iniciar em modo {'TESTE' if test_mode else 'REAL'}...\n")

    # Iniciar o listener com o config atualizado
    run_listener(config)
