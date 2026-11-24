import os
from integrations.whatsapp import set_reply_number
from bot.lead import handle_lead_message
from bot.admin import handle_admin_command


def handle_incoming_message(message, contact=None, metadata=None):
    from_phone = message.get('from', '')
    if not from_phone:
        return

    received_on = (metadata or {}).get('phone_number_id', '')
    set_reply_number(received_on)

    admin_id = os.getenv('ADMIN_PHONE_NUMBER_ID', os.getenv('WHATSAPP_PHONE_NUMBER_ID', ''))

    if received_on == admin_id:
        handle_admin_command(message, from_phone)
    else:
        handle_lead_message(message, from_phone)
