import os
import re

_state = {
    'runningAd': None,
    'adStartDate': None,
    'dailyBudget': None,
    'pendingConfirm': None,
    'pendingCreative': None,
    'adMap': {},
}

_counters = {'P': 0, 'V': 0}


def _load_ad_map_from_env():
    pattern = re.compile(r'^META_AD_ID_([PV]\d+)$')
    ad_map = {}
    for key, value in os.environ.items():
        m = pattern.match(key)
        if m and value:
            ad_map[m.group(1)] = value
    return ad_map


def _init():
    ad_map = _load_ad_map_from_env()
    _state['adMap'] = ad_map
    for code in ad_map:
        t = code[0]
        n = int(code[1:])
        if n > _counters[t]:
            _counters[t] = n


_init()


def get_state(key):
    return _state.get(key)


def set_state(key, value):
    _state[key] = value


def next_ad_code(type_char):
    _counters[type_char] += 1
    code = f"{type_char}{_counters[type_char]}"
    return code
