# Selfbot_listener.py

import logging
import warnings

# Suprimir warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

try:
    import discord
except ImportError:
    print("=" * 60)
    print("ERROR: discord.py-self is not installed!")
    print("=" * 60)
    print()
    print("Please run one of these commands:")
    print()
    print("Windows:")
    print("  pip uninstall discord discord.py discord.py-self -y")
    print("  pip install discord.py-self==2.0.0")
    print()
    print("Linux/Mac:")
    print("  pip3 uninstall discord discord.py discord.py-self -y")
    print("  pip3 install discord.py-self==2.0.0")
    print()
    print("Or run: FIX_INSTALL.bat")
    print("=" * 60)
    raise

from signal_parser import parse_signal
from trader import execute_trade
from telegram_alert import send_telegram_message, send_telegram_error

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class SignalClient(discord.Client):
    """Cliente Discord Selfbot para escutar sinais de trading"""
    
    def __init__(self, channel_id: str, config: dict, **kwargs):
        super().__init__(**kwargs)
        self.channel_id = str(channel_id).strip()
        self.config = config
        self.ready = False
        
    async def on_ready(self):
        """Evento chamado quando o bot está pronto"""
        self.ready = True
        logging.info("=" * 60)
        logging.info(f"✓ Connected as {self.user.name} (ID: {self.user.id})")
        logging.info(f"✓ Monitoring channel ID: {self.channel_id}")
        logging.info("=" * 60)
        
        # Tenta encontrar o canal
        try:
            channel = self.get_channel(int(self.channel_id))
            if channel:
                channel_name = getattr(channel, 'name', 'Unknown')
                guild_name = getattr(getattr(channel, 'guild', None), 'name', 'DM')
                logging.info(f"✓ Channel found: {channel_name} (Guild: {guild_name})")
            else:
                logging.warning(f"⚠ Channel {self.channel_id} not found in cache.")
                logging.warning("   The bot will still work if it has access to the channel.")
        except Exception as e:
            logging.warning(f"⚠ Could not verify channel: {e}")
    
    async def on_message(self, message):
        """Evento chamado quando uma mensagem é recebida"""
        try:
            # Ignora mensagens próprias
            if message.author.id == self.user.id:
                return
            
            # Verifica se é o canal correto
            if str(message.channel.id) != self.channel_id:
                return
            
            channel_name = getattr(message.channel, 'name', 'Unknown')
            logging.info("-" * 60)
            logging.info(f"📨 New message from {message.author.name} in #{channel_name}")
            logging.info(f"Content preview: {message.content[:100]}...")
            
            # Parse do sinal
            parsed = parse_signal(message.content)
            
            if not parsed:
                warn = "No valid signal was parsed from this message."
                logging.warning(f"⚠ {warn}")
                send_telegram_error(warn, self.config)
                return
            
            logging.info(f"✓ Signal parsed successfully: {parsed['pair']}")
            logging.info(f"  Entry: {parsed['entry']}")
            logging.info(f"  Targets: {parsed['targets']}")
            logging.info(f"  Stop Loss: {parsed['stop_loss']}")
            logging.info(f"  Side: {parsed.get('side', 'N/A')}")
            logging.info(f"  Leverage: {parsed.get('leverage', 'N/A')}")
            logging.info(f"  Market: {parsed.get('market', 'auto')}")
            
            # Executa o trade
            result = execute_trade(
                pair=parsed["pair"],
                entry_price=parsed["entry"],
                targets=parsed["targets"],
                stop_loss=parsed["stop_loss"],
                side=parsed.get("side"),
                leverage=parsed.get("leverage"),
                market=parsed.get("market"),
            )
            
            notify = f"Signal executed: {parsed['pair']} — {result}"
            logging.info(f"✓ {notify}")
            send_telegram_message(notify, self.config)
            
        except Exception as e:
            err = f"Listener error: {e}"
            logging.error(f"✗ {err}")
            import traceback
            logging.error(traceback.format_exc())
            send_telegram_error(err, self.config)
    
    async def on_error(self, event_method, *args, **kwargs):
        """Tratamento de erros do Discord"""
        logging.error(f"Discord error in {event_method}")
        import traceback
        logging.error(traceback.format_exc())

def run_listener(config: dict):
    """Inicia o listener do Discord Selfbot"""
    
    # Extrai configurações
    channel_id = config.get("channel_id", "").strip()
    discord_token = config.get("discord_token", "").strip()
    
    if not discord_token:
        logging.error("✗ Discord token not configured in config.json")
        raise ValueError("Discord token is required")
    
    if not channel_id:
        logging.error("✗ Channel ID not configured in config.json")
        raise ValueError("Channel ID is required")
    
    # Verifica se a biblioteca está correta
    if not hasattr(discord, 'Client'):
        print()
        print("=" * 60)
        print("ERROR: Wrong discord library detected!")
        print("=" * 60)
        print()
        print("You have the wrong version of discord library installed.")
        print("This bot requires 'discord.py-self', not 'discord.py'")
        print()
        print("To fix this, run:")
        print()
        print("  pip uninstall discord discord.py discord.py-self -y")
        print("  pip install discord.py-self==2.0.0")
        print()
        print("Or simply run: FIX_INSTALL.bat")
        print("=" * 60)
        raise AttributeError("Wrong discord library. Need discord.py-self==2.0.0")
    
    # Patch temporário para o bug de pending_payments
    # Isso deve ser feito ANTES de criar o client
    try:
        from discord import state
        original_parse_ready_supplemental = state.ConnectionState.parse_ready_supplemental
        
        def patched_parse_ready_supplemental(self, data):
            """Versão corrigida que trata pending_payments None"""
            # Garante que pending_payments nunca seja None
            if data and 'pending_payments' in data and data['pending_payments'] is None:
                data['pending_payments'] = []
            return original_parse_ready_supplemental(self, data)
        
        state.ConnectionState.parse_ready_supplemental = patched_parse_ready_supplemental
        logging.debug("Applied temporary patch for pending_payments bug")
    except Exception as e:
        logging.warning(f"Could not apply patch: {e}")
        logging.warning("If you get errors, try running: python patch_discord.py")
    
    # Tenta criar intents (pode não existir em algumas versões)
    client_kwargs = {}
    
    try:
        if hasattr(discord, 'Intents'):
            intents = discord.Intents.default()
            intents.messages = True
            intents.message_content = True
            intents.guilds = True
            intents.dm_messages = True
            intents.guild_messages = True
            client_kwargs['intents'] = intents
    except Exception as e:
        logging.debug(f"Could not configure intents: {e}")
    
    # Cria e executa o client
    try:
        client = SignalClient(
            channel_id=channel_id,
            config=config,
            **client_kwargs
        )
        
        # Para selfbot, simplesmente rode sem o parâmetro bot
        # A biblioteca discord.py-self já sabe que é um selfbot
        logging.info("Connecting to Discord...")
        client.run(discord_token)
        
    except discord.LoginFailure:
        logging.error("=" * 60)
        logging.error("✗ Failed to login to Discord")
        logging.error("=" * 60)
        logging.error("")
        logging.error("Possible causes:")
        logging.error("1. Invalid token - Get a new one from Discord")
        logging.error("2. Using a BOT token instead of USER token")
        logging.error("3. Token expired - Tokens can expire after some time")
        logging.error("")
        logging.error("How to get a valid USER token:")
        logging.error("1. Open Discord in browser")
        logging.error("2. Press Ctrl+Shift+I (Developer Tools)")
        logging.error("3. Go to Network tab")
        logging.error("4. Press F5 to reload")
        logging.error("5. Look for requests with 'api/v9'")
        logging.error("6. Find 'authorization' in headers")
        logging.error("7. Copy the entire value")
        logging.error("=" * 60)
        raise
    except Exception as e:
        logging.error(f"✗ Failed to start Discord client: {e}")
        raise