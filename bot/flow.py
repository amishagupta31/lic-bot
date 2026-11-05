FLOW_STEPS = [
    {
        'key': 'intro',
        'type': 'message',
        'text': (
            "Namaste! 🙏\n\n"
            "LIC ke saath kaam ki jaankari lene ke liye dhanyavaad.\n\n"
            "Bas kuch chhote sawaal, 1 minute lagega."
        ),
    },
    {
        'key': 'name',
        'type': 'text_input',
        'text': "Aapka naam kya hai?",
    },
    {
        'key': 'district',
        'type': 'buttons',
        'text': "Aap kis district se hain?",
        'buttons': [
            {'id': 'district_karnal', 'title': 'Karnal'},
            {'id': 'district_other', 'title': 'Doosra district'},
        ],
    },
    {
        'key': 'age',
        'type': 'buttons',
        'text': "Kya aapki umar 18 saal ya usse zyada hai?",
        'buttons': [
            {'id': 'age_yes', 'title': 'Haan'},
            {'id': 'age_no', 'title': 'Nahi'},
        ],
    },
    {
        'key': 'education',
        'type': 'buttons',
        'text': "Kya aapne 10th pass ki hai aur aapke paas 10th ka certificate hai?",
        'buttons': [
            {'id': 'edu_cert', 'title': 'Haan, certificate hai'},
            {'id': 'edu_no_cert', 'title': 'Pass hai, certificate nahi'},
            {'id': 'edu_fail', 'title': '10th pass nahi'},
        ],
    },
    {
        'key': 'motivation',
        'type': 'buttons',
        'text': "Kya aap apni zindagi mein kuch accha aur apna khud ka karna chahte hain?",
        'buttons': [
            {'id': 'mot_yes', 'title': 'Haan'},
            {'id': 'mot_maybe', 'title': 'Abhi soch raha/rahi hoon'},
        ],
    },
    {
        'key': 'commission',
        'type': 'buttons',
        'text': (
            "Ek zaroori baat: yeh fixed salary wali naukri nahi hai.\n\n"
            "Aapki kamai aapki mehnat par depend karti hai. "
            "Aap apne boss khud hain aur apni marzi se kaam kar sakte hain.\n\n"
            "Kya aap tayyar hain?"
        ),
        'buttons': [
            {'id': 'comm_yes', 'title': 'Haan, tayyar hoon'},
            {'id': 'comm_maybe', 'title': 'Pehle aur jaanna hai'},
            {'id': 'comm_no', 'title': 'Nahi, salary chahiye'},
        ],
    },
    {
        'key': 'daily_time',
        'type': 'buttons',
        'text': "Kya aap roz 1-2 ghante is kaam ke liye nikaal sakte hain?",
        'buttons': [
            {'id': 'time_yes', 'title': 'Haan'},
            {'id': 'time_maybe', 'title': 'Kabhi-kabhi'},
            {'id': 'time_no', 'title': 'Nahi'},
        ],
    },
]

_NQ_MSG = (
    "Dhanyavaad {{naam}} ji. Abhi yeh mauka sirf Karnal district ke "
    "18+ aur 10th pass logon ke liye hai. Aapke samay ke liye shukriya. 🙏"
)

EXIT_MESSAGES = {
    'district_other': _NQ_MSG,
    'age_no':         _NQ_MSG,
    'edu_fail':       _NQ_MSG,
    'comm_no':        "Bilkul samajh aata hai! Koi baat nahi. Shubhkamnayen! 🙏",
    'time_no':        "Samajh aata hai. Jab time mile, toh zaroor sochiega. Hum yahan hain! 🙏",
}

COMM_MAYBE_EXPLANATION = (
    "Bilkul! Thodi aur jankari:\n\n"
    "📋 *Process:*\n"
    "1. Registration (₹860 ek baar)\n"
    "2. IC-38 training (free)\n"
    "3. Exam (online)\n"
    "4. LIC appointment letter\n\n"
    "✅ Stipend guaranteed (government backed)\n"
    "✅ Ghar se kaam, flexible timing\n\n"
    "Ab batayein, tayyar hain?"
)
