SCORES = {
    'intro_yes': 5,
    'gender_yes': 0,
    'gender_no': None,       # gate fail
    'district_karnal': 10,
    'district_other': None,  # gate fail
    'age_yes': 10,
    'age_no': None,          # gate fail
    'edu_cert': 20,
    'edu_no_cert': 10,
    'edu_fail': None,        # gate fail
    'mot_yes': 20,
    'mot_maybe': 10,
    'comm_yes': 20,
    'comm_maybe': 10,
    'comm_no': 0,
    'time_yes': 15,
    'time_maybe': 8,
    'time_no': 0,
}

GATE_CHECKS = [
    {'key': 'gender',    'fail_id': 'gender_no',      'label': 'Gender'},
    {'key': 'district',  'fail_id': 'district_other', 'label': 'District'},
    {'key': 'age',       'fail_id': 'age_no',         'label': 'Age 18-70'},
    {'key': 'education', 'fail_id': 'edu_fail',       'label': 'Education'},
]

GATE_FAILURES = {
    'gender':    'gender_no',
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
