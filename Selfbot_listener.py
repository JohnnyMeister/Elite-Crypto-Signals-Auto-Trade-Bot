import discord
from signal_parser import parse_signal

class MyClient(discord.Client):
    def __init__(self, canal_id):
        super().__init__()
        self.canal_id = canal_id

    async def on_ready(self):
        print(f"✅ Ligado como {self.user}")

    async def on_message(self, message):
        if message.channel.id != self.canal_id:
            return

        if message.author.id != self.user.id:
            print(f"📨 Nova mensagem no canal: {message.content[:30]}...")
            parsed = parse_signal(message.content)

            if parsed is False:
                print("⚠️ Nenhum sinal válido encontrado na mensagem.")
            else:
                print("📥 Sinal processado com sucesso.")

def run_listener(config):
    client = MyClient(canal_id=config["discord_channel_id"])
    client.run(config["discord_token"])  # sem o bot=False
