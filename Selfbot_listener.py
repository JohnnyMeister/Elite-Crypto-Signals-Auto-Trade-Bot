# Selfbot_listener.py
import discord
from signal_parser import parse_signal
from telegram_alert import send_telegram_message
from trader import execute_trade
import logging

logging.basicConfig(level=logging.INFO)

class MyClient(discord.Client):
    def __init__(self, canal_id, config, **options):
        super().__init__(**options)
        self.canal_id = canal_id
        self.config = config

    async def on_ready(self):
        logging.info(f'✅ Logado como {self.user}')

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return  # Ignora mensagens do próprio user

        if message.channel.id != self.canal_id:
            return

        logging.info(f"📩 Mensagem recebida: {message.content[:80]}...")

        parsed = parse_signal(message.content)
        if not parsed:
            logging.info("⚠️ Nenhum sinal válido encontrado nesta mensagem.")
            return

        logging.info(f"📊 Sinal válido encontrado: {parsed}")

        try:
            result = execute_trade(
                pair=parsed['pair'],
                entry_price=parsed['price'],
                targets=parsed.get('targets'),
                stop_loss=parsed.get('stop_loss')
            )
            alert_message = (
                f"💰 Trade executada: {parsed['pair']} a {parsed['price']}\n"
                f"TP: {parsed.get('targets')}\nSL: {parsed.get('stop_loss')}\n"
                f"Modo teste: {self.config['test_mode']}\nResultado: {result}"
            )
        except Exception as e:
            alert_message = f"❌ Falha ao executar trade para {parsed['pair']}: {str(e)}"

        send_telegram_message(self.config, alert_message)


def run_listener(config):
    client = MyClient(
        canal_id=int(config["discord_channel_id"]),
        config=config,
        heartbeat_timeout=60
    )

    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    client.run(config["discord_token"])
