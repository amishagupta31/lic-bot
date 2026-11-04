import os
import requests

GRAPH_URL = "https://graph.facebook.com/v20.0"


def _headers():
    return {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json",
    }


def _phone_id():
    return os.getenv('WHATSAPP_PHONE_NUMBER_ID')


def send_message(to, text):
    url = f"{GRAPH_URL}/{_phone_id()}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text, "preview_url": False},
    }
    r = requests.post(url, json=payload, headers=_headers())
    r.raise_for_status()
    return r.json()


def send_buttons(to, text, buttons):
    """buttons: list of {'id': str, 'title': str} (max 3, title max 20 chars)"""
    url = f"{GRAPH_URL}/{_phone_id()}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": b["id"], "title": b["title"][:20]}}
                    for b in buttons[:3]
                ]
            },
        },
    }
    r = requests.post(url, json=payload, headers=_headers())
    r.raise_for_status()
    return r.json()


def get_media_url(media_id):
    r = requests.get(
        f"{GRAPH_URL}/{media_id}",
        headers=_headers(),
    )
    r.raise_for_status()
    return r.json().get('url')


def download_media(media_url):
    """Download media bytes from WhatsApp CDN."""
    r = requests.get(media_url, headers=_headers())
    r.raise_for_status()
    return r.content, r.headers.get('content-type', 'image/jpeg')
