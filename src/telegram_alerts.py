import requests

from src.config import CHAT_ID, TELEGRAM_TOKEN


def send_telegram_message(message: str) -> None:
    if not TELEGRAM_TOKEN or not CHAT_ID:
        raise RuntimeError(
            "TELEGRAM_TOKEN ou CHAT_ID manquant dans la configuration."
        )

    url = (
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    )

    try:
        response = requests.post(
            url,
            json={
                "chat_id": CHAT_ID,
                "text": message,
            },
            timeout=20,
        )
    except requests.RequestException:
        raise RuntimeError(
            "Impossible de joindre Telegram."
        ) from None

    if not response.ok:
        raise RuntimeError(
            f"Telegram a refusé l'envoi : HTTP {response.status_code}."
        )

    try:
        payload = response.json()
    except ValueError:
        raise RuntimeError(
            "Réponse Telegram non valide."
        ) from None

    if not payload.get("ok"):
        raise RuntimeError(
            "Telegram n'a pas confirmé l'envoi du message."
        )