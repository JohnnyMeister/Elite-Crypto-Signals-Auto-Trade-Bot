# Selfbot_listener.py

import discord
import logging
from signal_parser import parse_signal
from trader import execute_trade
from telegram_alert import send_telegram_message

logging.basicConfig(level=logging.INFO)

class MyClient(discord.Client):
    def __init__(self, canal_id, config):
        super().__init__()
        self.canal_id = canal_id
        self.config = config

    async def on_ready(self):
        logging.info(f"🤖 Ligado como {self.user} (ID: {self.user.id})")

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.channel.id != int(self.canal_id):
            return

        logging.info(f"📥 Nova mensagem recebida de {message.author}: {message.content[:60]}...")

        parsed = parse_signal(message.content)
        if not parsed:
            logging.warning("❌ Nenhum sinal válido foi extraído.")
            return

        result = execute_trade(
            pair=parsed["pair"],
            entry_price=parsed["entry"],
            targets=parsed["targets"],
            stop_loss=parsed["stop_loss"]
        )

        notify = f"📈 Sinal executado: {parsed['pair']} — {result}"
        logging.info(notify)

        if self.config.get("telegram_token") and self.config.get("telegram_chat_id"):
            send_telegram_message(notify, self.config)

def run_listener(config):
    client = MyClient(
        canal_id=config["canal_id"],
        config=config
    )
    # Selfbots usam o token da própria conta (modo user), sem "bot=" nem intents
    client.run(config["discord_token"])
