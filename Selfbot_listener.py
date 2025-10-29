# Selfbot_listener.py

import discord
import logging

from signal_parser import parse_signal
from trader import execute_trade
from telegram_alert import send_telegram_message

logging.basicConfig(level=logging.INFO)


class SignalClient(discord.Client):
    def __init__(self, channel_id: int, config: dict):
        super().__init__()
        self.channel_id = channel_id
        self.config = config

    async def on_ready(self):
        logging.info(f"Connected as {self.user} (ID: {self.user.id})")

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.channel.id != int(self.channel_id):
            return

        logging.info(f"New message from {message.author}: {message.content[:60]}...")

        parsed = parse_signal(message.content)
        if not parsed:
            logging.warning("No valid signal was parsed.")
            return

        result = execute_trade(
            pair=parsed["pair"],
            entry_price=parsed["entry"],
            targets=parsed["targets"],
            stop_loss=parsed["stop_loss"],
        )

        notify = f"Signal executed: {parsed['pair']} — {result}"
        logging.info(notify)

        if self.config.get("telegram_token") and self.config.get("telegram_chat_id"):
            send_telegram_message(notify, self.config)


def run_listener(config: dict):
    client = SignalClient(
        channel_id=config["channel_id"],
        config=config,
    )
    # Uses a user token (selfbot style). No 'bot=' prefix or intents are used here.
    client.run(config["discord_token"])
