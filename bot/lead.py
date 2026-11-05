import re
from bot.flow import FLOW_STEPS, EXIT_MESSAGES, COMM_MAYBE_EXPLANATION
from bot.scoring import score_session, GATE_FAILURES
from bot.sessions import get_session, set_session, delete_session, new_session
from bot.notifications import send_lead_alert
from integrations.whatsapp import send_message, send_buttons
from integrations.sheets import save_lead

QUESTION_RE = re.compile(
    r'\b(kya|kitna|kitni|kitne|kaisa|kaise|kyun|kab|kahan|salary|paise|income|stipend|fees?|kamai)\b|\?',
    re.IGNORECASE,
)

AD_CODE_RE = re.compile(r'\bhi\s+([PV]\d+)\b', re.IGNORECASE)


def _is_question(text):
    return bool(QUESTION_RE.search(text))


def _get_approved_answer(text):
    t = text.lower()
    if any(w in t for w in ['stipend', 'salary', 'kamai', 'income', 'paise', 'kitna']):
        return (
            "💰 *Kamai details:*\n\n"
            "• Year 1: ₹7,000/mahina stipend\n"
            "• Year 2: ₹6,000/mahina\n"
            "• Year 3: ₹5,000/mahina\n"
            "+ Har policy par alag commission\n\n"
            "Yeh fixed salary nahi hai — stipend + commission structure hai."
        )
    if any(w in t for w in ['fees', 'fee', 'registration', '860']):
        return (
            "📋 *Fees:*\n\n"
            "Registration fee sirf *₹860* (ek baar).\n"
            "IC-38 training bilkul free hai."
        )
    return (
        "Yeh ek LIC government-backed yojana hai.\n"
        "Koi bhi sawaal ho, poochh sakte hain! 😊"
    )


def _send_step(to, step):
    if step['type'] == 'buttons':
        send_buttons(to, step['text'], step['buttons'])
    else:
        send_message(to, step['text'])


def _is_message_step(step):
    return step.get('type') == 'message'


def handle_lead_message(message, from_phone):
    session = get_session(from_phone)

    # New session — extract ad code from "Hi P1"
    if not session:
        body = ''
        if message.get('type') == 'text':
            body = (message.get('text') or {}).get('body', '').strip()

        m = AD_CODE_RE.search(body)
        ad_code = m.group(1).upper() if m else None
        session = new_session(ad_code=ad_code)
        set_session(from_phone, session)

    step_index = session['step']
    if step_index >= len(FLOW_STEPS):
        return

    current_step = FLOW_STEPS[step_index]

    # Auto-advance 'message' type steps (send and immediately move to next)
    if _is_message_step(current_step):
        send_message(from_phone, current_step['text'])
        _advance(from_phone, session)
        return

    msg_type = message.get('type')

    # ── Button reply ──────────────────────────────────────────────────────────
    if msg_type == 'interactive':
        button_id = (message.get('interactive') or {}).get('button_reply', {}).get('id', '')
        _handle_button(from_phone, session, button_id)
        return

    # ── Text message ──────────────────────────────────────────────────────────
    if msg_type == 'text':
        text = ((message.get('text') or {}).get('body') or '').strip()

        # Question detection (skip for name step)
        if current_step['key'] != 'name' and _is_question(text):
            answer = _get_approved_answer(text)
            send_message(from_phone, answer)
            _send_step(from_phone, current_step)
            return

        # Accept text for text_input steps (name)
        if current_step['type'] == 'text_input':
            session['answers'][current_step['key']] = text
            session['retryCount'] = 0
            set_session(from_phone, session)
            _advance(from_phone, session)
            return

        # Text given for a button step — retry
        session['retryCount'] = session.get('retryCount', 0) + 1
        set_session(from_phone, session)
        if session['retryCount'] >= 3:
            _advance(from_phone, session)
            return
        send_message(from_phone, "Buttons use karein please 👆")
        _send_step(from_phone, current_step)


def _handle_button(from_phone, session, button_id):
    step_index = session['step']
    current_step = FLOW_STEPS[step_index]
    answers = session['answers']

    # comm_maybe — show explanation, re-ask same step
    if button_id == 'comm_maybe':
        send_message(from_phone, COMM_MAYBE_EXPLANATION)
        _send_step(from_phone, current_step)
        return

    # Gate fail exit message
    if button_id in EXIT_MESSAGES:
        answers[current_step['key']] = button_id
        set_session(from_phone, session)
        naam = answers.get('name', 'Aap')
        exit_msg = EXIT_MESSAGES[button_id].replace('{naam}', naam)
        send_message(from_phone, exit_msg)

        # Save not-qualified lead
        score, category, flags = score_session(answers)
        save_lead(from_phone, answers, session, score, 'NOT_QUALIFIED', flags or [button_id])
        delete_session(from_phone)
        return

    answers[current_step['key']] = button_id
    session['retryCount'] = 0
    set_session(from_phone, session)
    _advance(from_phone, session)


def _advance(from_phone, session):
    next_index = session['step'] + 1
    session['step'] = next_index
    set_session(from_phone, session)

    if next_index >= len(FLOW_STEPS):
        _complete_flow(from_phone, session)
        return

    next_step = FLOW_STEPS[next_index]
    if _is_message_step(next_step):
        send_message(from_phone, next_step['text'])
        _advance(from_phone, session)
        return

    _send_step(from_phone, next_step)


def _complete_flow(from_phone, session):
    answers = session['answers']
    score, category, flags = score_session(answers)

    name = answers.get('name', 'Aap')

    if category in ('HOT', 'WARM'):
        msg = (
            f"Dhanyavaad {name} ji! Hamari team aapko jaldi call karegi. "
            f"Apna 10th certificate tayyar rakhein. 🙏"
        )
    else:
        msg = (
            f"Dhanyavaad {name} ji. Abhi yeh mauka sirf Karnal district ke "
            f"18+ aur 10th pass logon ke liye hai. Aapke samay ke liye shukriya. 🙏"
        )

    send_message(from_phone, msg)
    save_lead(from_phone, answers, session, score, category, flags)

    if category in ('HOT', 'WARM'):
        send_lead_alert(from_phone, answers, score, category, session.get('adCode'), flags)

    delete_session(from_phone)
