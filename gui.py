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

    token = simpledialog.askstring("Token Discord", "Insere o teu token de utilizador do Discord:")
    canal = simpledialog.askstring("Canal ID", "Insere o ID do canal do Discord onde os sinais chegam:")
    telegram_token = simpledialog.askstring("Telegram Token", "Insere o token do teu bot do Telegram:")
    telegram_chat_id = simpledialog.askstring("Chat ID Telegram", "Insere o ID do teu chat do Telegram:")
    api_key = simpledialog.askstring("Coinbase API Key", "Insere a tua API Key da Coinbase:")
    api_secret = simpledialog.askstring("Coinbase API Secret", "Insere a tua API Secret da Coinbase:")
    fixed_amount = simpledialog.askstring("Valor por entrada", "Quanto USDC queres usar por trade (ex: 50)?")

    config = {
        "discord_token": token,
        "discord_channel_id": int(canal),
        "telegram_token": telegram_token,
        "telegram_chat_id": telegram_chat_id,
        "coinbase_api_key": api_key,
        "coinbase_api_secret": api_secret,
        "fixed_amount": float(fixed_amount),
        "test_mode": test_mode
    }

    save_config(config)
    messagebox.showinfo("✅ Sucesso", "Configuração salva com sucesso!")
    return config
