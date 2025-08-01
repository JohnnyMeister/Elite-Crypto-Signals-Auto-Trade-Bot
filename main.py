import asyncio
import sys

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


import os
import json
import tkinter as tk
from tkinter import messagebox
from subprocess import run
from Selfbot_listener import run_listener

CONFIG_PATH = "config.json"

def ask_test_mode():
    root = tk.Tk()
    root.withdraw()
    response = messagebox.askyesno("Modo Teste", "Deseja iniciar o programa em MODO TESTE?")
    return response

def create_default_config(test_mode: bool):
    # Passa o valor de test_mode como argumento para o GUI
    from gui import show_gui
    show_gui(test_mode)
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError("Configuração não criada.")
    with open(CONFIG_PATH, "r+") as f:
        config = json.load(f)
        config["test_mode"] = test_mode
        f.seek(0)
        json.dump(config, f, indent=2)
        f.truncate()

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    test_mode = ask_test_mode()

    if not os.path.exists(CONFIG_PATH):
        print("🔧 Criando nova configuração...")
        create_default_config(test_mode)
    else:
        # Atualiza apenas o valor de test_mode
        with open(CONFIG_PATH, "r+") as f:
            config = json.load(f)
            config["test_mode"] = test_mode
            f.seek(0)
            json.dump(config, f, indent=2)
            f.truncate()

    config = load_config()
    print("🚀 Iniciando o bot com as configurações:")
    print(json.dumps(config, indent=2))

    run_listener(config)
