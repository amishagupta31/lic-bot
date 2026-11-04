import os
from integrations.whatsapp import send_message

ANSWER_LABELS = {
    'intro_yes':        'Interested ✅',
    'gender_yes':       'Mahila ✅',
    'gender_no':        'Mahila nahi ❌',
    'district_karnal':  'Karnal ✅',
    'district_other':   'Other District ❌',
    'age_yes':          '18-70 ✅',
    'age_no':           'Outside 18-70 ❌',
    'edu_cert':         'Certificate hai ✅',
    'edu_no_cert':      'No Certificate ⚠️',
    'edu_fail':         '10th fail ❌',
    'mot_yes':          'Motivated ✅',
    'mot_maybe':        'Maybe ⚠️',
    'comm_yes':         'Commission OK ✅',
    'comm_maybe':       'Needs info ⚠️',
    'comm_no':          'Ruchi nahi ❌',
    'time_yes':         'Time hai ✅',
    'time_maybe':       'Limited time ⚠️',
    'time_no':          'Time nahi ❌',
}

EMOJI = {'HOT': '🔥', 'WARM': '⚡', 'COLD': '❄️', 'NOT_QUALIFIED': '❌'}


def _get_admin_phones():
    phones = []
    primary = os.getenv('CLIENT_PHONE')
    if primary:
        phones.append(primary)
    secondary = os.getenv('CLIENT_PHONE_2')
    if secondary:
        phones.append(secondary)
    return phones


def _format_answers(answers):
    lines = []
    for key, val in answers.items():
        if key == 'name':
            lines.append(f"Naam: {val}")
        else:
            label = ANSWER_LABELS.get(val, val)
            lines.append(f"{key.capitalize()}: {label}")
    return '\n'.join(lines)


def send_lead_alert(phone, answers, score, category, ad_code, flags=None):
    if category == 'COLD':
        return

    emoji = EMOJI.get(category, '📋')
    name = answers.get('name', 'Unknown')
    ad = ad_code or 'Unknown'

    lines = [f"{emoji} *{category} LEAD — {ad}*\n"]
    lines.append(f"Naam: {name}")
    lines.append(f"Number: +{phone}")
    lines.append(f"Score: {score}/100")
    if flags:
        lines.append(f"Flags: {', '.join(flags)}")
    lines.append("")
    lines.append(_format_answers({k: v for k, v in answers.items() if k != 'name'}))

    text = '\n'.join(lines)

    for admin in _get_admin_phones():
        try:
            send_message(admin, text)
        except Exception as e:
            print(f'Alert send error to {admin}: {e}')
