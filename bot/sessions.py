import json

_SESSION_FILE = '/tmp/lic_sessions.json'


def _load():
    try:
        with open(_SESSION_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data):
    try:
        with open(_SESSION_FILE, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass


def get_session(phone):
    return _load().get(phone)


def set_session(phone, session):
    data = _load()
    data[phone] = session
    _save(data)


def delete_session(phone):
    data = _load()
    data.pop(phone, None)
    _save(data)


def new_session(ad_code=None):
    return {
        'step': 0,
        'answers': {},
        'adCode': ad_code,
        'retryCount': 0,
    }
