"""
Pytest tests for LIC Bima Sakhi WhatsApp webhook.
Run: pytest -v test_whatsapp_webhook.py
"""
import os, time, pytest

os.environ.setdefault('WHATSAPP_TOKEN', 'test_token')
os.environ.setdefault('WHATSAPP_PHONE_NUMBER_ID', '1462039916984005')
os.environ.setdefault('WHATSAPP_VERIFY_TOKEN', 'lic_bot_verify_123')
os.environ.setdefault('CLIENT_PHONE', '910000000001')   # fake admin — 919883728616 becomes a lead
os.environ.setdefault('GOOGLE_SCRIPT_URL', 'http://localhost/fake')

import main as webhook_app

@pytest.fixture
def client():
    webhook_app.app.config['TESTING'] = True
    return webhook_app.app.test_client()


def _msg_payload(text, from_number='919883728616', msg_id=None):
    return {
        'object': 'whatsapp_business_account',
        'entry': [{
            'id': '17967846115283341',
            'changes': [{
                'field': 'messages',
                'value': {
                    'messaging_product': 'whatsapp',
                    'metadata': {
                        'display_phone_number': '15551385766',
                        'phone_number_id': '1462039916984005'
                    },
                    'contacts': [{'profile': {'name': 'Test User'}, 'wa_id': from_number}],
                    'messages': [{
                        'from': from_number,
                        'id': msg_id or f'wamid.test_{int(time.time())}',
                        'timestamp': str(int(time.time())),
                        'type': 'text',
                        'text': {'body': text}
                    }]
                }
            }]
        }]
    }


def _status_payload(status='delivered'):
    return {
        'object': 'whatsapp_business_account',
        'entry': [{
            'changes': [{
                'field': 'messages',
                'value': {
                    'messaging_product': 'whatsapp',
                    'statuses': [{
                        'id': 'wamid.test_status',
                        'status': status,
                        'recipient_id': '919883728616',
                        'timestamp': str(int(time.time()))
                    }]
                }
            }]
        }]
    }


# ── TC-01: Incoming message triggers reply ───────────────────────────────────
def test_incoming_message_triggers_reply(client):
    from unittest.mock import patch, MagicMock
    sent = []

    def mock_send(to, text):
        sent.append({'to': to, 'text': text})
        return {'messages': [{'id': 'wamid.mock'}]}

    with patch('bot.admin.send_message', mock_send), \
         patch('bot.lead.send_message', mock_send), \
         patch('bot.notifications.send_message', mock_send):
        r = client.post('/webhook', json=_msg_payload('Hii'))
        time.sleep(0.5)

    assert r.status_code == 200
    assert len(sent) >= 1, "Bot did not send any reply"
    assert sent[0]['to'] == '919883728616'


# ── TC-02: Correct sender extracted ─────────────────────────────────────────
def test_correct_sender_extracted(client):
    from unittest.mock import patch
    captured = {}

    def mock_send(to, text):
        captured['to'] = to
        return {'messages': [{'id': 'wamid.mock'}]}

    with patch('bot.admin.send_message', mock_send), \
         patch('bot.lead.send_message', mock_send), \
         patch('bot.notifications.send_message', mock_send):
        r = client.post('/webhook', json=_msg_payload('Hello Bot', from_number='919777888999'))
        time.sleep(0.5)

    assert r.status_code == 200
    assert captured.get('to') == '919777888999'


# ── TC-03: Delivered status must NOT trigger reply ───────────────────────────
def test_delivered_status_no_reply(client, monkeypatch):
    sent = []

    def mock_send(to, text):
        sent.append(text)

    monkeypatch.setattr('integrations.whatsapp.send_message', mock_send)

    r = client.post('/webhook', json=_status_payload('delivered'))
    time.sleep(0.3)

    assert r.status_code == 200
    assert len(sent) == 0, "Bot should NOT reply to delivery status"


# ── TC-04: Missing messages field — no crash ────────────────────────────────
def test_missing_messages_no_crash(client):
    payload = {
        'object': 'whatsapp_business_account',
        'entry': [{
            'changes': [{
                'field': 'messages',
                'value': {'statuses': []}
            }]
        }]
    }
    r = client.post('/webhook', json=payload)
    assert r.status_code == 200


# ── TC-05: Wrong object type returns 404 ────────────────────────────────────
def test_wrong_object_returns_404(client):
    r = client.post('/webhook', json={'object': 'page', 'entry': []})
    assert r.status_code == 404


# ── TC-06: WhatsApp API failure — error logged, no crash ────────────────────
def test_api_failure_no_crash(client, monkeypatch):
    def mock_send_error(to, text):
        raise Exception("WhatsApp API down")

    monkeypatch.setattr('integrations.whatsapp.send_message', mock_send_error)

    r = client.post('/webhook', json=_msg_payload('Hi'))
    assert r.status_code == 200   # bot still returns 200 to Meta


# ── TC-07: Webhook GET verification ─────────────────────────────────────────
def test_webhook_verification(client):
    r = client.get('/webhook', query_string={
        'hub.mode': 'subscribe',
        'hub.verify_token': 'lic_bot_verify_123',
        'hub.challenge': 'test_challenge_123'
    })
    assert r.status_code == 200
    assert b'test_challenge_123' in r.data


# ── TC-08: Wrong verify token returns 403 ───────────────────────────────────
def test_wrong_verify_token_forbidden(client):
    r = client.get('/webhook', query_string={
        'hub.mode': 'subscribe',
        'hub.verify_token': 'wrong_token',
        'hub.challenge': 'abc'
    })
    assert r.status_code == 403
