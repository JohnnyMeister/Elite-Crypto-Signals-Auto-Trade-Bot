# main.py

import os
import json
import sys
import warnings

# Suprimir TODOS os warnings de deprecação
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Importar asyncio DEPOIS de suprimir warnings
import asyncio
import platform

# Não configurar event loop policy - usar o padrão do sistema
# Isso evita warnings de deprecação no Python 3.14+

from Selfbot_listener import run_listener

CONFIG_FILE = "config.json"

def create_default_config():
    """Cria um arquivo de configuração padrão"""
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
        "target_selection": {
            "T1": True,
            "T2": True,
            "T3": False,
            "T4": False
        }
    }
    
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
        print(f"✓ {CONFIG_FILE} created successfully!")
        print("Edit it with your credentials and settings, then run again.")
        return True
    except Exception as e:
        print(f"✗ Error creating config file: {e}")
        return False

def load_config():
    """Carrega e valida a configuração"""
    if not os.path.exists(CONFIG_FILE):
        print(f"✗ {CONFIG_FILE} not found. Creating default configuration...")
        create_default_config()
        sys.exit(1)
    
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            config = json.load(f)
        
        # Validação básica
        required_fields = ["discord_token", "channel_id"]
        missing = [field for field in required_fields if not config.get(field)]
        
        if missing:
            print(f"✗ Missing required fields in config: {', '.join(missing)}")
            print("Please edit config.json and add the required information.")
            sys.exit(1)
        
        # Avisos para campos opcionais
        if not config.get("binance_api_key") or not config.get("binance_api_secret"):
            print("⚠ Warning: Binance API credentials not configured. Trading will not work.")
        
        if not config.get("telegram_token") or not config.get("telegram_chat_id"):
            print("⚠ Warning: Telegram credentials not configured. Notifications disabled.")
        
        return config
        
    except json.JSONDecodeError as e:
        print(f"✗ Error parsing {CONFIG_FILE}: {e}")
        print("Please check the JSON syntax in your config file.")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error loading config: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    print("=" * 60)
    print("  Discord Signal Trading Bot - Selfbot Mode")
    print("=" * 60)
    print()
    
    # Carrega configuração
    config = load_config()
    
    # Mostra informações
    test_mode = config.get("test_mode", True)
    trade_mode = config.get("trade_mode", "auto")
    
    print(f"Mode: {'TEST (no real trades)' if test_mode else 'LIVE (real trading!)'}")
    print(f"Trade Mode: {trade_mode.upper()}")
    print(f"Channel ID: {config['channel_id']}")
    print(f"Target Selection: T1={config['target_selection']['T1']}, "
          f"T2={config['target_selection']['T2']}, "
          f"T3={config['target_selection']['T3']}, "
          f"T4={config['target_selection']['T4']}")
    print()
    print("Starting Discord selfbot listener...")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    try:
        run_listener(config)
    except KeyboardInterrupt:
        print("\n\nBot stopped by user.")
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()