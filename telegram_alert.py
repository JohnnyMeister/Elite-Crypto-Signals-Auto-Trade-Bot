# telegram_alert.py

import requests
import logging

def _post(url, data):
    """Helper para fazer POST requests com tratamento de erros"""
    try:
        return requests.post(url, data=data, timeout=15)
    except requests.exceptions.Timeout:
        logging.error("Telegram request timeout")
        return None
    except requests.exceptions.ConnectionError:
        logging.error("Telegram connection error")
        return None
    except Exception as e:
        logging.error(f"Telegram HTTP error: {e}")
        return None

def send_telegram_message(message: str, config: dict) -> bool:
    """
    Envia uma mensagem para o Telegram.
    
    Args:
        message: Texto da mensagem
        config: Dicionário de configuração com telegram_token e telegram_chat_id
    
    Returns:
        True se enviou com sucesso, False caso contrário
    """
    telegram_token = config.get("telegram_token", "").strip()
    telegram_chat_id = config.get("telegram_chat_id", "").strip()
    
    if not telegram_token or not telegram_chat_id:
        logging.debug("Telegram not configured. Message not sent.")
        return False
    
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    data = {
        "chat_id": telegram_chat_id,
        "text": message,
        "parse_mode": "HTML",
    }
    
    resp = _post(url, data)
    
    if not resp:
        logging.error("Failed to send Telegram message: no response")
        return False
    
    if resp.status_code != 200:
        try:
            error_msg = resp.json().get("description", resp.text)
            logging.error(f"Failed to send Telegram message: {error_msg}")
        except Exception:
            logging.error(f"Failed to send Telegram message: HTTP {resp.status_code}")
        return False
    
    logging.debug("Message sent to Telegram successfully")
    return True

def send_telegram_error(message: str, config: dict) -> bool:
    """
    Envia uma mensagem de erro para o Telegram com formatação específica.
    
    Args:
        message: Texto do erro
        config: Dicionário de configuração
    
    Returns:
        True se enviou com sucesso, False caso contrário
    """
    formatted_message = f"🚨 <b>[ERROR]</b>\n{message}"
    return send_telegram_message(formatted_message, config)

def send_telegram_success(message: str, config: dict) -> bool:
    """
    Envia uma mensagem de sucesso para o Telegram com formatação específica.
    
    Args:
        message: Texto da mensagem
        config: Dicionário de configuração
    
    Returns:
        True se enviou com sucesso, False caso contrário
    """
    formatted_message = f"✅ <b>[SUCCESS]</b>\n{message}"
    return send_telegram_message(formatted_message, config)

def send_telegram_warning(message: str, config: dict) -> bool:
    """
    Envia uma mensagem de aviso para o Telegram com formatação específica.
    
    Args:
        message: Texto do aviso
        config: Dicionário de configuração
    
    Returns:
        True se enviou com sucesso, False caso contrário
    """
    formatted_message = f"⚠️ <b>[WARNING]</b>\n{message}"
    return send_telegram_message(formatted_message, config)