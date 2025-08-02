# main.py

import os
import json
import time
from gui import show_gui
from Selfbot_listener import run_listener

CONFIG_FILE = "config.json"

# Verifica se config existe, senão chama o GUI para criar
if not os.path.exists(CONFIG_FILE):
    print("🔧 Config.json não encontrado. A abrir GUI para criação...")
    show_gui()  # Abre GUI para criar config

# Verifica se o arquivo foi criado corretamente após o GUI
if not os.path.exists(CONFIG_FILE):
    raise FileNotFoundError("❌ Configuração não criada corretamente. O programa será encerrado.")

# Aguarda um momento para garantir que o arquivo esteja salvo
time.sleep(1)

# Carrega a configuração
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

# Executa o listener principal
run_listener(config)
