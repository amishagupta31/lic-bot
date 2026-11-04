import re
from integrations.whatsapp import send_message
from integrations.meta_ads import pause_ad, resume_ad, update_budget, get_ad_stats
from bot.reports import generate_report
from utils.state import get_state, set_state

_last_action = None

SWITCH_RE = re.compile(r'^(video|poster|v|p)\s*(\d+)\s*(chalu karo|on karo|start karo)$', re.IGNORECASE)
STATS_RE  = re.compile(r'^(video|poster|v|p)\s*(\d+)$', re.IGNORECASE)
BUDGET_RE = re.compile(r'budget\s*(?:₹|rs\.?)?\s*(\d+)', re.IGNORECASE)


def handle_admin_command(message, from_phone):
    global _last_action

    msg_type = message.get('type', '')

    if msg_type in ('image', 'video', 'document'):
        from integrations.creative import handle_creative_launch
        handle_creative_launch(message, from_phone)
        return

    if msg_type != 'text':
        return

    text = ((message.get('text') or {}).get('body') or '').strip().lower()

    # ── Confirmation ──────────────────────────────────────────────────────────
    pending = get_state('pendingConfirm')
    if pending and text in ('haan', 'haan ✅', 'ha', 'yes'):
        set_state('pendingConfirm', None)
        try:
            _execute(from_phone, pending)
        except Exception as e:
            print(f'Admin action error: {e}')
            send_message(from_phone, f"❌ Kaam nahi ho paya.\n\nReason: {e}")
        return

    if pending and text in ('nahi', 'nahi ❌', 'no'):
        set_state('pendingConfirm', None)
        send_message(from_phone, "Theek hai, koi action nahi liya. ✅")
        return

    # ── Run pending creative ──────────────────────────────────────────────────
    if 'run' in text and get_state('pendingCreative'):
        from integrations.creative import launch_pending_creative
        launch_pending_creative(from_phone, text)
        return

    # ── Switch ad ─────────────────────────────────────────────────────────────
    m = SWITCH_RE.match(text)
    if m:
        t = 'V' if m.group(1).lower().startswith('v') else 'P'
        ad_code = f"{t}{m.group(2)}"
        _confirm_switch(from_phone, ad_code)
        return

    # ── Pause ─────────────────────────────────────────────────────────────────
    if 'band karo' in text and 'sab' not in text:
        current = get_state('runningAd')
        if not current:
            send_message(from_phone, "Abhi koi ad chal nahi raha.")
            return
        set_state('pendingConfirm', {'action': 'pause', 'adCode': current})
        send_message(from_phone, f"Ad {current} band karna hai? HAAN / NAHI")
        return

    if 'sab band karo' in text:
        set_state('pendingConfirm', {'action': 'pause_all'})
        send_message(from_phone, "Saare ads band karne hain? HAAN / NAHI")
        return

    # ── Budget ────────────────────────────────────────────────────────────────
    bm = BUDGET_RE.search(text)
    if bm:
        amount = int(bm.group(1))
        set_state('pendingConfirm', {'action': 'budget', 'amount': amount})
        send_message(from_phone, f"Daily budget ₹{amount} karna hai? HAAN / NAHI")
        return

    # ── Report ────────────────────────────────────────────────────────────────
    if text == 'report':
        report = generate_report('live')
        send_message(from_phone, report)
        return

    # ── Stats ─────────────────────────────────────────────────────────────────
    sm = STATS_RE.match(text)
    if sm:
        t = 'V' if sm.group(1).lower().startswith('v') else 'P'
        ad_code = f"{t}{sm.group(2)}"
        stats = get_ad_stats(ad_code)
        send_message(from_phone, _format_stats(ad_code, stats))
        return

    # ── Undo ──────────────────────────────────────────────────────────────────
    if text == 'undo':
        try:
            _handle_undo(from_phone)
        except Exception as e:
            send_message(from_phone, f"❌ Undo nahi ho paya.\n\nReason: {e}")
        return

    send_message(
        from_phone,
        "Yeh commands use kar sakte hain:\n\n"
        "• *video 2 chalu karo* — V2 chalu karo\n"
        "• *band karo* — current ad band karo\n"
        "• *sab band karo* — sab band karo\n"
        "• *budget ₹100* — budget change karo\n"
        "• *report* — abhi ki report dekho\n"
        "• *video 2* — V2 ki stats dekho\n"
        "• *undo* — last action undo karo",
    )


def _confirm_switch(from_phone, new_code):
    current = get_state('runningAd')
    start_date = get_state('adStartDate')

    warning = ''
    if current and start_date:
        import datetime
        days = (datetime.datetime.now() - datetime.datetime.fromisoformat(start_date)).days
        if days < 7:
            warning = f"⚠️ *Warning:* {current} sirf {days} din se chal raha hai (min 7 din recommended).\n\n"

    msg = (
        f"{warning}{current} band karke {new_code} chalu karna hai? HAAN / NAHI"
        if current else
        f"{new_code} chalu karna hai? HAAN / NAHI"
    )
    set_state('pendingConfirm', {'action': 'switch', 'from': current, 'to': new_code})
    send_message(from_phone, msg)


def _execute(from_phone, pending):
    global _last_action
    action = pending['action']

    if action == 'switch':
        resume_ad(pending['to'])
        _last_action = {'type': 'switch', 'from': pending.get('from'), 'to': pending['to']}
        set_state('runningAd', pending['to'])

        import datetime
        set_state('adStartDate', datetime.datetime.now().isoformat())

        old = pending.get('from')
        if old and old != pending['to']:
            try:
                pause_ad(old)
            except Exception as e:
                raise Exception(
                    f"{pending['to']} live hai lekin {old} band nahi hua — dono par paisa kharch ho sakta hai. "
                    f"Ads Manager mein {old} band karein. ({e})"
                )
        send_message(
            from_phone,
            f"✅ {pending['to']} ab live hai!" + (f" {old} band ho gaya." if old else ""),
        )

    elif action == 'pause':
        pause_ad(pending['adCode'])
        _last_action = {'type': 'pause', 'adCode': pending['adCode']}
        set_state('runningAd', None)
        send_message(from_phone, f"✅ {pending['adCode']} band ho gaya.")

    elif action == 'pause_all':
        current = get_state('runningAd')
        if current:
            pause_ad(current)
        _last_action = {'type': 'pause_all', 'adCode': current}
        set_state('runningAd', None)
        send_message(from_phone, "✅ Saare ads band ho gaye.")

    elif action == 'budget':
        update_budget(pending['amount'])
        _last_action = {'type': 'budget', 'oldAmount': get_state('dailyBudget'), 'newAmount': pending['amount']}
        set_state('dailyBudget', pending['amount'])
        send_message(from_phone, f"✅ Daily budget ₹{pending['amount']} ho gaya.")

    elif action == 'launch_creative':
        from integrations.creative import launch_creative_after_confirm
        launch_creative_after_confirm(from_phone, pending)


def _handle_undo(from_phone):
    global _last_action
    if not _last_action:
        send_message(from_phone, "Koi recent action nahi hai jo undo ho sake.")
        return

    t = _last_action['type']
    if t == 'switch':
        if _last_action.get('from'):
            resume_ad(_last_action['from'])
        pause_ad(_last_action['to'])
        set_state('runningAd', _last_action.get('from'))
        send_message(
            from_phone,
            (f"✅ Undo ho gaya. {_last_action['from']} wapas live, {_last_action['to']} band."
             if _last_action.get('from')
             else f"✅ Undo ho gaya. {_last_action['to']} band ho gaya."),
        )
    elif t in ('pause', 'pause_all'):
        if _last_action.get('adCode'):
            resume_ad(_last_action['adCode'])
            set_state('runningAd', _last_action['adCode'])
            send_message(from_phone, f"✅ Undo ho gaya. {_last_action['adCode']} wapas live.")
    elif t == 'budget':
        update_budget(_last_action['oldAmount'])
        set_state('dailyBudget', _last_action['oldAmount'])
        send_message(from_phone, f"✅ Undo ho gaya. Budget wapas ₹{_last_action['oldAmount']}.")

    _last_action = None


def _format_stats(ad_code, stats):
    if not stats:
        return f"{ad_code} ke liye koi data nahi mila."
    return (
        f"📊 *{ad_code} Stats*\n\n"
        f"Status: {stats.get('status', 'N/A')}\n"
        f"Spend: ₹{stats.get('spend', 0)}\n"
        f"Leads: {stats.get('leads', 0)}\n"
        f"Hot Leads: {stats.get('hotLeads', 0)}\n"
        f"Cost/Hot Lead: ₹{stats.get('costPerHotLead') or 'N/A'}"
    )
