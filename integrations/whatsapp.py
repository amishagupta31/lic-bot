import os
import requests
from contextvars import ContextVar

GRAPH_URL = "https://graph.facebook.com/v20.0"

# Set per-request so replies always go from the number that received the message
_reply_number_id: ContextVar[str] = ContextVar('reply_number_id', default='')


def set_reply_number(phone_number_id: str):
    _reply_number_id.set(phone_number_id)


def _headers():
    return {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json",
    }


def _phone_id():
    return _reply_number_id.get() or os.getenv('WHATSAPP_PHONE_NUMBER_ID')


def send_message(to, text):
    url = f"{GRAPH_URL}/{_phone_id()}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text, "preview_url": False},
    }
    r = requests.post(url, json=payload, headers=_headers())
    if not r.ok:
        print(f"WhatsApp send_message error {r.status_code}: {r.text}")
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
    if not r.ok:
        print(f"WhatsApp send_buttons error {r.status_code}: {r.text}")
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
