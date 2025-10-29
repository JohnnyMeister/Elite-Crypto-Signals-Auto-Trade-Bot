# main.py

import asyncio, platform, os, json
from Selfbot_listener import run_listener

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

CONFIG_FILE = "config.json"

def create_default_config():
    default_config = {
        "binance_api_key": "",
        "binance_api_secret": "",
        "gemini_api_key": "",
        "gemini_model": "gemini-1.5-flash",
        "telegram_token": "",
        "telegram_chat_id": "",
        "discord_token": "",
        "channel_id": "",
        "test_mode": True,
        "trade_mode": "auto",
        "futures_default_leverage": 5,
        "futures_working_type": "MARK_PRICE",
        "target_selection": { "T1": True, "T2": True, "T3": False, "T4": False }
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=4)
    print("config.json created. Edit it with your credentials and settings, then run again.")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        create_default_config()
        raise SystemExit(1)
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    config = load_config()
    run_listener(config)
