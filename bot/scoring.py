SCORES = {
    'district_karnal': 25,
    'district_other':  None,  # gate fail
    'age_yes':         0,     # gate only
    'age_no':          None,  # gate fail
    'edu_cert':        25,
    'edu_no_cert':     10,
    'edu_fail':        None,  # gate fail
    'mot_yes':         5,
    'mot_maybe':       2,
    'comm_yes':        25,
    'comm_maybe':      12,
    'comm_no':         0,
    'time_yes':        20,
    'time_maybe':      10,
    'time_no':         0,
}

GATE_CHECKS = [
    {'key': 'district',  'fail_id': 'district_other', 'label': 'District'},
    {'key': 'age',       'fail_id': 'age_no',         'label': 'Age 18+'},
    {'key': 'education', 'fail_id': 'edu_fail',       'label': 'Education'},
]

GATE_FAILURES = {
    'district':  'district_other',
    'age':       'age_no',
    'education': 'edu_fail',
}


def score_session(answers):
    total = 0
    flags = []

    for gate in GATE_CHECKS:
        answer = answers.get(gate['key'])
        if answer == gate['fail_id']:
            flags.append(gate['label'])

    if flags:
        return 0, 'NOT_QUALIFIED', flags

    for key, answer in answers.items():
        s = SCORES.get(answer, 0)
        if s is not None:
            total += s

    if total >= 85:
        category = 'HOT'
    elif total >= 60:
        category = 'WARM'
    else:
        category = 'COLD'

    return total, category, flags
