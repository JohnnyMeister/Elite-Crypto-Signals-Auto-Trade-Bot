# gui.py

import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os

CONFIG_FILE = "config.json"

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None

def show_gui(test_mode=False):
    root = tk.Tk()
    root.withdraw()

    mode_text = "MODO TESTE" if test_mode else "MODO REAL"
    messagebox.showinfo("Modo de Execução", f"O programa será iniciado em {mode_text}.")

    token = simpledialog.askstring("Token Discord", "Insere o teu token de utilizador do Discord:")
    canal = simpledialog.askstring("ID do Canal Discord", "Insere o ID do canal onde os sinais chegam:")
    telegram_token = simpledialog.askstring("Token Telegram", "Insere o token do bot do Telegram:")
    telegram_chat_id = simpledialog.askstring("Chat ID Telegram", "Insere o ID do teu chat do Telegram:")
    api_key = simpledialog.askstring("Binance API Key", "Insere a tua API Key da Binance:")
    api_secret = simpledialog.askstring("Binance API Secret", "Insere a tua API Secret da Binance:")
    fixed_amount = simpledialog.askstring("Valor por trade (USDT)", "Quanto USDT queres usar por entrada (ex: 50)?")

    try:
        config = {
            "discord_token": token.strip(),
            "canal_id": int(canal.strip()),
            "telegram_token": telegram_token.strip(),
            "telegram_chat_id": telegram_chat_id.strip(),
            "binance_api_key": api_key.strip(),
            "binance_api_secret": api_secret.strip(),
            "fixed_amount": float(fixed_amount.strip()),
            "test_mode": test_mode
        }
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao validar os dados: {e}")
        return

    save_config(config)
    messagebox.showinfo("✅ Sucesso", "Configuração salva com sucesso!")
    return config
