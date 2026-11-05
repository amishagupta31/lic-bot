import json
import os
import requests

_SESSION_TTL = 86400  # 24 hours

_redis_url   = None
_redis_token = None
_local: dict = {}   # fallback if Redis not configured


def _redis():
    global _redis_url, _redis_token
    if _redis_url is None:
        _redis_url   = os.getenv('UPSTASH_REDIS_REST_URL', '')
        _redis_token = os.getenv('UPSTASH_REDIS_REST_TOKEN', '')
    return bool(_redis_url and _redis_token)


def _rget(key):
    r = requests.get(
        f"{_redis_url}/get/{key}",
        headers={"Authorization": f"Bearer {_redis_token}"},
        timeout=3,
    )
    val = r.json().get('result')
    return json.loads(val) if val else None


def _rset(key, value):
    requests.post(
        f"{_redis_url}/set/{key}",
        headers={"Authorization": f"Bearer {_redis_token}", "Content-Type": "application/json"},
        json={"value": json.dumps(value), "ex": _SESSION_TTL},
        timeout=3,
    )


def _rdel(key):
    requests.get(
        f"{_redis_url}/del/{key}",
        headers={"Authorization": f"Bearer {_redis_token}"},
        timeout=3,
    )


def get_session(phone):
    if _redis():
        return _rget(f"session:{phone}")
    return _local.get(phone)


def set_session(phone, session):
    if _redis():
        _rset(f"session:{phone}", session)
    else:
        _local[phone] = session


def delete_session(phone):
    if _redis():
        _rdel(f"session:{phone}")
    else:
        _local.pop(phone, None)


def new_session(ad_code=None):
    return {
        'step': 0,
        'answers': {},
        'adCode': ad_code,
        'retryCount': 0,
    }
