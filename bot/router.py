from utils.auth import is_admin
from bot.lead import handle_lead_message
from bot.admin import handle_admin_command


def handle_incoming_message(message, contact=None, metadata=None):
    from_phone = message.get('from', '')

    if not from_phone:
        return

    if is_admin(from_phone):
        handle_admin_command(message, from_phone)
    else:
        handle_lead_message(message, from_phone)
