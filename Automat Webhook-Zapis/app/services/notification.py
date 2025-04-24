import os
import logging
import json
import aiohttp
from dotenv import load_dotenv
from typing import Dict, Any

# Załaduj zmienne środowiskowe
load_dotenv()

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfiguracja Discord
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_USERNAME = os.getenv("DISCORD_USERNAME", "Webhook Bot")
DISCORD_AVATAR_URL = os.getenv("DISCORD_AVATAR_URL", "")

async def send_notification_discord(subject: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wysyła powiadomienie na Discord z danymi formularza.
    
    Args:
        subject: Temat powiadomienia
        form_data: Dane przesłane w formularzu
    
    Returns:
        Słownik z informacją o statusie wysyłki
    """
    if not DISCORD_WEBHOOK_URL:
        logger.error("Brak URL webhooks Discord. Nie można wysłać powiadomienia.")
        return {"status": "failed", "error": "Brak URL webhooks Discord"}
    
    # Przygotowanie wiadomości
    fields = []
    for key, value in form_data.items():
        fields.append({
            "name": key,
            "value": str(value),
            "inline": True
        })
    
    # Tworzenie embeda Discord
    embed = {
        "title": subject,
        "description": "Nowe zgłoszenie z formularza!",
        "color": 3447003,  # niebieski kolor
        "fields": fields,
        "timestamp": f"{__import__('datetime').datetime.utcnow().isoformat()}Z"
    }
    
    # Dane do wysłania
    payload = {
        "username": DISCORD_USERNAME,
        "embeds": [embed]
    }
    
    if DISCORD_AVATAR_URL:
        payload["avatar_url"] = DISCORD_AVATAR_URL
    
    try:
        # Wysyłanie wiadomości
        async with aiohttp.ClientSession() as session:
            async with session.post(
                DISCORD_WEBHOOK_URL, 
                json=payload
            ) as response:
                if response.status == 204:  # Discord zwraca 204 No Content przy sukcesie
                    logger.info("Powiadomienie wysłane na Discord")
                    return {"status": "sent", "webhook_url": DISCORD_WEBHOOK_URL}
                else:
                    error_text = await response.text()
                    logger.error(f"Błąd podczas wysyłania na Discord: {response.status} - {error_text}")
                    return {"status": "failed", "error": f"Kod statusu: {response.status} - {error_text}"}
    
    except Exception as e:
        logger.error(f"Błąd podczas wysyłania powiadomienia na Discord: {str(e)}")
        return {"status": "failed", "error": str(e)}

# Alias dla zachowania zgodności z istniejącym kodem
send_notification_email = send_notification_discord 