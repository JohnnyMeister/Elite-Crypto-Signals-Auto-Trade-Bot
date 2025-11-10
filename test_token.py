#!/usr/bin/env python3
"""
Script para testar se o token do Discord está válido
"""

import json
import sys
import warnings

warnings.filterwarnings('ignore')

def load_token():
    """Carrega o token do config.json"""
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        token = config.get("discord_token", "").strip()
        if not token:
            print("❌ No discord_token found in config.json")
            sys.exit(1)
        return token
    except FileNotFoundError:
        print("❌ config.json not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        sys.exit(1)

def test_token(token):
    """Testa o token do Discord"""
    print("=" * 60)
    print("  Discord Token Tester")
    print("=" * 60)
    print()
    
    # Importa discord
    try:
        import discord
        print("✓ discord.py-self imported successfully")
    except ImportError:
        print("❌ discord.py-self not installed")
        print("   Run: pip install discord.py-self==2.0.0")
        sys.exit(1)
    
    # Cria client simples
    print("✓ Creating Discord client...")
    
    try:
        # Tenta com intents
        if hasattr(discord, 'Intents'):
            intents = discord.Intents.default()
            intents.message_content = True
            client = discord.Client(intents=intents)
        else:
            client = discord.Client()
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        sys.exit(1)
    
    print("✓ Client created")
    print()
    print("🔄 Testing connection to Discord...")
    print("   (This may take a few seconds)")
    print()
    
    # Variável para armazenar resultado
    test_result = {"success": False, "error": None}
    
    @client.event
    async def on_ready():
        """Quando conectar com sucesso"""
        print("=" * 60)
        print("✅ SUCCESS! Token is valid!")
        print("=" * 60)
        print()
        print(f"Connected as: {client.user.name}#{client.user.discriminator}")
        print(f"User ID: {client.user.id}")
        print()
        
        # Mostra servidores
        guilds = client.guilds
        if guilds:
            print(f"Your account is in {len(guilds)} servers:")
            for guild in guilds[:5]:  # Mostra apenas 5 primeiros
                print(f"  • {guild.name} (ID: {guild.id})")
            if len(guilds) > 5:
                print(f"  ... and {len(guilds) - 5} more")
        else:
            print("Your account is not in any servers")
        
        print()
        print("=" * 60)
        test_result["success"] = True
        await client.close()
    
    # Tenta conectar
    try:
        client.run(token)
    except discord.LoginFailure:
        print("=" * 60)
        print("❌ LOGIN FAILED - Invalid Token")
        print("=" * 60)
        print()
        print("Your token is invalid or expired.")
        print()
        print("How to get a valid token:")
        print("1. Open Discord in your browser (desktop app may not work)")
        print("2. Press Ctrl+Shift+I to open Developer Tools")
        print("3. Go to the 'Network' tab")
        print("4. Press F5 to reload the page")
        print("5. Look for requests to 'api/v9' or 'api/v10'")
        print("6. Click on one and find 'authorization' in Request Headers")
        print("7. Copy the ENTIRE value (it's usually very long)")
        print("8. Paste it in config.json as 'discord_token'")
        print()
        print("=" * 60)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print("=" * 60)
        print(f"❌ ERROR: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    if test_result["success"]:
        print("\n✅ Your token works perfectly!")
        print("You can now run: python main.py")
        sys.exit(0)
    else:
        print("\n❌ Connection test failed")
        sys.exit(1)

if __name__ == "__main__":
    token = load_token()
    test_token(token)