#!/usr/bin/env python3
"""
Script para verificar se todas as dependências estão instaladas corretamente
"""

import sys

def check_python_version():
    """Verifica versão do Python"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"   ✗ Python {version.major}.{version.minor} detected")
        print(f"   ✗ Python 3.8 or higher is required")
        return False
    print(f"   ✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_discord():
    """Verifica instalação do discord.py-self"""
    print("\n🔍 Checking discord.py-self...")
    try:
        import discord
        
        # Verifica se tem os atributos necessários
        if not hasattr(discord, 'Client'):
            print("   ✗ discord module found but missing 'Client' class")
            print("   ✗ Wrong discord library installed")
            print("\n   Fix: pip uninstall discord discord.py -y && pip install discord.py-self==2.0.0")
            return False
        
        # Tenta obter versão
        version = getattr(discord, '__version__', 'unknown')
        print(f"   ✓ discord.py-self installed (version: {version})")
        
        # Verifica Client
        print("   ✓ discord.Client available")
        
        # Verifica Intents (opcional)
        if hasattr(discord, 'Intents'):
            print("   ✓ discord.Intents available")
        else:
            print("   ⚠ discord.Intents not available (may work anyway)")
        
        return True
        
    except ImportError as e:
        print(f"   ✗ discord module not found: {e}")
        print("\n   Fix: pip install discord.py-self==2.0.0")
        return False
    except Exception as e:
        print(f"   ✗ Error checking discord: {e}")
        return False

def check_binance():
    """Verifica instalação do python-binance"""
    print("\n🔍 Checking python-binance...")
    try:
        from binance.client import Client
        print("   ✓ python-binance installed")
        return True
    except ImportError:
        print("   ✗ python-binance not found")
        print("\n   Fix: pip install python-binance")
        return False

def check_requests():
    """Verifica instalação do requests"""
    print("\n🔍 Checking requests...")
    try:
        import requests
        version = getattr(requests, '__version__', 'unknown')
        print(f"   ✓ requests installed (version: {version})")
        return True
    except ImportError:
        print("   ✗ requests not found")
        print("\n   Fix: pip install requests")
        return False

def check_gemini():
    """Verifica instalação do google-generativeai (opcional)"""
    print("\n🔍 Checking google-generativeai (optional)...")
    try:
        import google.generativeai as genai
        print("   ✓ google-generativeai installed")
        return True
    except ImportError:
        print("   ⚠ google-generativeai not found (optional)")
        print("   ℹ Install with: pip install google-generativeai")
        return True  # Não é crítico

def check_config():
    """Verifica se config.json existe"""
    print("\n🔍 Checking config.json...")
    try:
        import os
        import json
        
        if not os.path.exists("config.json"):
            print("   ⚠ config.json not found")
            print("   ℹ Run main.py to create a default config")
            return True  # Não é erro crítico
        
        with open("config.json", "r") as f:
            config = json.load(f)
        
        print("   ✓ config.json found")
        
        # Verifica campos importantes
        if config.get("discord_token"):
            print("   ✓ discord_token configured")
        else:
            print("   ⚠ discord_token not configured")
        
        if config.get("channel_id"):
            print("   ✓ channel_id configured")
        else:
            print("   ⚠ channel_id not configured")
        
        return True
        
    except json.JSONDecodeError:
        print("   ✗ config.json has invalid JSON syntax")
        return False
    except Exception as e:
        print(f"   ⚠ Could not check config: {e}")
        return True

def main():
    """Função principal"""
    print("=" * 60)
    print("  Discord Selfbot Trading Bot - Installation Check")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Discord Library", check_discord),
        ("Binance Library", check_binance),
        ("Requests Library", check_requests),
        ("Gemini AI (Optional)", check_gemini),
        ("Configuration", check_config),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            results.append(check_func())
        except Exception as e:
            print(f"\n✗ Unexpected error in {name}: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"\n✓ All checks passed! ({passed}/{total})")
        print("\nYou're ready to run: python main.py")
    else:
        print(f"\n⚠ Some checks failed ({passed}/{total} passed)")
        print("\nPlease fix the issues above before running the bot.")
    
    print("\n" + "=" * 60)
    
    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())