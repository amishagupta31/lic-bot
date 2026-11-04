_sessions = {}


def get_session(phone):
    return _sessions.get(phone)


def set_session(phone, session):
    _sessions[phone] = session


def delete_session(phone):
    _sessions.pop(phone, None)


def new_session(ad_code=None):
    return {
        'step': 0,
        'answers': {},
        'adCode': ad_code,
        'retryCount': 0,
    }
