import os
import requests
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))


def format_lead_date():
    return datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')


def _script_url():
    return os.getenv('GOOGLE_SCRIPT_URL')


def init_sheet():
    url = _script_url()
    if not url:
        print('⚠️  GOOGLE_SCRIPT_URL not set — leads will not be saved to sheet')
        return
    print('✅ Google Sheet ready (via Apps Script)')


def save_lead(phone, answers, session, score, category, flags=None):
    url = _script_url()
    if not url:
        print(f'Sheet not configured — lead {phone} not saved')
        return

    name = answers.get('name', '')
    ad_code = session.get('adCode', '')
    flags_str = ', '.join(flags) if flags else ''
    date_str = format_lead_date()

    row = {
        'phone': phone,
        'name': name,
        'district': answers.get('district', ''),
        'age': answers.get('age', ''),
        'education': answers.get('education', ''),
        'motivation': answers.get('motivation', ''),
        'commission': answers.get('commission', ''),
        'daily_time': answers.get('daily_time', ''),
        'score': score,
        'category': category,
        'ad_code': ad_code,
        'gender': answers.get('gender', ''),
        'flags': flags_str,
        'date': date_str,
    }

    try:
        r = requests.post(url, json=row, timeout=10)
        r.raise_for_status()
        print(f'✅ Lead saved: {phone} — {category}')
    except Exception as e:
        print(f'❌ Sheet save error: {e}')


def get_leads_stats(days=1, ad_code=None):
    """Fetch stats from Apps Script."""
    url = _script_url()
    if not url:
        return None

    params = {'action': 'stats', 'days': days}
    if ad_code:
        params['adCode'] = ad_code

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f'Sheet stats error: {e}')
        return None
