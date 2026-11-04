import os
import sys
import threading
from flask import Flask, request
from dotenv import load_dotenv

# Force UTF-8 output on Windows so emoji in print() don't crash
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()

REQUIRED_ENV = ['WHATSAPP_TOKEN', 'WHATSAPP_PHONE_NUMBER_ID', 'WHATSAPP_VERIFY_TOKEN', 'CLIENT_PHONE']
missing = [k for k in REQUIRED_ENV if not os.getenv(k)]
if missing:
    print(f"❌ Missing in .env: {', '.join(missing)}")
    exit(1)

from bot.router import handle_incoming_message
from jobs.cron import start_cron_jobs
from integrations.sheets import init_sheet
from integrations.meta_ads import sync_running_ad

app = Flask(__name__)


@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode      = request.args.get('hub.mode')
    token     = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == os.getenv('WHATSAPP_VERIFY_TOKEN'):
        print('✅ Webhook verified')
        return challenge, 200
    return 'Forbidden', 403


@app.route('/webhook', methods=['POST'])
def webhook():
    body = request.get_json(silent=True) or {}
    if body.get('object') != 'whatsapp_business_account':
        return '', 404

    # Reply 200 immediately — Meta resends to slow webhooks
    def process():
        try:
            entry  = (body.get('entry') or [{}])[0]
            change = (entry.get('changes') or [{}])[0]
            value  = change.get('value') or {}
            msgs   = value.get('messages') or []
            if msgs:
                contacts = value.get('contacts') or []
                handle_incoming_message(
                    msgs[0],
                    contacts[0] if contacts else None,
                    value.get('metadata') or {},
                )
        except Exception as e:
            print(f'Webhook processing error: {e}')

    threading.Thread(target=process, daemon=True).start()
    return '', 200


@app.route('/')
def health():
    return 'LIC Bot is running ✅'


if __name__ == '__main__':
    start_cron_jobs()
    init_sheet()
    sync_running_ad()
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
