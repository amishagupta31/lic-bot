FLOW_STEPS = [
    {
        'key': 'intro',
        'type': 'buttons',
        'text': (
            "Namaste! 🙏\n\n"
            "*LIC Bima Sakhi Yojana* mein aapka swagat hai!\n\n"
            "Yeh ek khaas yojana hai jisme Haryana ki mahilayein ghar se kaam karke "
            "achhi kamai kar sakti hain.\n\n"
            "Kya aap is baare mein jaanna chahti hain?"
        ),
        'buttons': [
            {'id': 'intro_yes', 'title': 'Haan, batao'},
            {'id': 'intro_no', 'title': 'Abhi nahi'},
        ],
    },
    {
        'key': 'name',
        'type': 'text_input',
        'text': "Bahut achha! 😊\n\nSabse pehle, aapka *poora naam* batayein:",
    },
    {
        'key': 'gender',
        'type': 'buttons',
        'text': "Dhanyavaad! Yeh yojana sirf *mahilaon ke liye* hai.\n\nKya aap mahila hain?",
        'buttons': [
            {'id': 'gender_yes', 'title': 'Haan, mahila hoon'},
            {'id': 'gender_no', 'title': 'Nahi'},
        ],
    },
    {
        'key': 'district',
        'type': 'buttons',
        'text': (
            "Yeh yojana abhi *Karnal district* ke liye hai.\n\n"
            "Kya aap Karnal se hain?"
        ),
        'buttons': [
            {'id': 'district_karnal', 'title': 'Haan, Karnal se hoon'},
            {'id': 'district_other', 'title': 'Nahi, kisi aur se'},
        ],
    },
    {
        'key': 'age',
        'type': 'buttons',
        'text': (
            "Yojana ke liye umar *18 se 70 saal* ke beech honi chahiye.\n\n"
            "Kya aapki umar is range mein hai?"
        ),
        'buttons': [
            {'id': 'age_yes', 'title': 'Haan, is range mein'},
            {'id': 'age_no', 'title': 'Nahi'},
        ],
    },
    {
        'key': 'education',
        'type': 'buttons',
        'text': "Aapki padhai ke baare mein batayein:",
        'buttons': [
            {'id': 'edu_cert', 'title': 'Certificate hai'},
            {'id': 'edu_no_cert', 'title': 'Certificate nahi'},
            {'id': 'edu_fail', 'title': '10th pass nahi'},
        ],
    },
    {
        'key': 'motivation',
        'type': 'buttons',
        'text': (
            "LIC Bima Sakhi mein *Agent* ban sakte hain aur ghar se kaam kar sakte hain.\n\n"
            "Kya aap apni income badhana chahti hain?"
        ),
        'buttons': [
            {'id': 'mot_yes', 'title': 'Haan, bilkul'},
            {'id': 'mot_maybe', 'title': 'Abhi soch rahi hoon'},
        ],
    },
    {
        'key': 'commission',
        'type': 'buttons',
        'text': (
            "💰 *Kamai ke baare mein:*\n\n"
            "• Pehle saal: *₹7,000/mahina* stipend\n"
            "• Doosre saal: *₹6,000/mahina*\n"
            "• Teesre saal: *₹5,000/mahina*\n"
            "+ Har policy par *commission* alag se\n\n"
            "24 policies target, registration fee *₹860*\n\n"
            "Kya yeh aapko theek lagta hai?"
        ),
        'buttons': [
            {'id': 'comm_yes', 'title': 'Haan, theek hai'},
            {'id': 'comm_maybe', 'title': 'Pehle aur jaanna hai'},
            {'id': 'comm_no', 'title': 'Nahi, ruchi nahi'},
        ],
    },
    {
        'key': 'daily_time',
        'type': 'buttons',
        'text': "Kya aap *roz 2-3 ghante* is kaam ko de sakti hain?",
        'buttons': [
            {'id': 'time_yes', 'title': 'Haan, de sakti hoon'},
            {'id': 'time_maybe', 'title': 'Kabhi kabhi'},
            {'id': 'time_no', 'title': 'Nahi, mushkil hai'},
        ],
    },
]

EXIT_MESSAGES = {
    'intro_no': "Theek hai! Jab bhi ready hon, hum yahan hain. 😊",
    'gender_no': (
        "Samajh aata hai. Yeh yojana abhi *mahilaon ke liye* hi hai.\n\n"
        "Agar aapke parivaar mein koi mahila interested ho, toh unhe bata sakte hain! 🙏"
    ),
    'district_other': (
        "Abhi yeh yojana sirf *Karnal district* mein chal rahi hai.\n\n"
        "Jab aapke area mein shuru ho, hum zaroor batayenge! 🙏"
    ),
    'age_no': (
        "Samajh aata hai. Yojana ke liye *18-70 saal* ki umar zaroori hai.\n\n"
        "Agar koi eligible ho, unhe batayein! 🙏"
    ),
    'edu_fail': (
        "Koi baat nahi! Padhai continue kar sakte hain.\n\n"
        "10th pass karne ke baad hume zaroor contact karein! 🙏"
    ),
    'comm_no': "Bilkul samajh aata hai! Koi baat nahi. Shubhkamnayen! 🙏",
    'time_no': (
        "Samajh aata hai. Jab time mile, toh zaroor sochiega.\n\n"
        "Hum yahan hain! 🙏"
    ),
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
    "Ab batayein, interested hain?"
)
