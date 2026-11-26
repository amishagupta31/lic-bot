import json
import os
import requests

_SESSION_TTL  = 86400        # 24 hours  — active flow (mid-form)
_HISTORY_TTL  = 15 * 86400  # 15 days  — completed lead record

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
    r = requests.post(
        f"{_redis_url}/pipeline",
        headers={"Authorization": f"Bearer {_redis_token}", "Content-Type": "application/json"},
        json=[["GET", key]],
        timeout=5,
    )
    if not r.ok:
        print(f"Redis GET error {r.status_code}: {r.text}")
        return None
    results = r.json()
    val = results[0].get('result') if results else None
    return json.loads(val) if val else None


def _rset(key, value, ttl=None):
    ttl = ttl or _SESSION_TTL
    r = requests.post(
        f"{_redis_url}/pipeline",
        headers={"Authorization": f"Bearer {_redis_token}", "Content-Type": "application/json"},
        json=[["SET", key, json.dumps(value), "EX", ttl]],
        timeout=5,
    )
    if not r.ok:
        print(f"Redis SET error {r.status_code}: {r.text}")


def _rdel(key):
    requests.post(
        f"{_redis_url}/pipeline",
        headers={"Authorization": f"Bearer {_redis_token}", "Content-Type": "application/json"},
        json=[["DEL", key]],
        timeout=5,
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


# ── Conversation history (returning users) ───────────────────────────────────

def save_history(phone, answers, category):
    """Store completed lead so bot recognises returning users."""
    record = {'answers': answers, 'category': category}
    if _redis():
        _rset(f"history:{phone}", record, ttl=_HISTORY_TTL)
    else:
        _local[f"history:{phone}"] = record


def get_history(phone):
    if _redis():
        return _rget(f"history:{phone}")
    return _local.get(f"history:{phone}")
