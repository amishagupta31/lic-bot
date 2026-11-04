from datetime import datetime, timezone, timedelta
from integrations.sheets import get_leads_stats
from integrations.meta_ads import get_spend_since, get_all_ad_stats
from utils.state import get_state

IST = timezone(timedelta(hours=5, minutes=30))


def generate_report(mode='live'):
    now = datetime.now(IST).strftime('%d %b %Y, %H:%M')
    stats = get_leads_stats(days=1) or {}
    spend = get_spend_since(days=1)

    total   = stats.get('total', 0)
    hot     = stats.get('hot', 0)
    warm    = stats.get('warm', 0)
    not_q   = stats.get('not_qualified', 0)

    running_ad = get_state('runningAd') or 'None'

    spend_str = f"₹{spend:.2f}" if spend is not None else "N/A"
    cost_per_hot = (
        f"₹{spend / hot:.2f}" if (spend and hot) else "N/A"
    )

    return (
        f"📊 *LIC Bot Report*\n"
        f"_{now}_\n\n"
        f"*Aaj ke Leads:*\n"
        f"• Total Leads: *{total}*\n"
        f"• Hot Leads: *{hot}* 🔥\n"
        f"• Warm Leads: *{warm}* ⚡\n"
        f"• Not Qualified: *{not_q}* ❌\n\n"
        f"*Meta Ads:*\n"
        f"• Aaj ka Spend: *{spend_str}*\n"
        f"• Cost/Hot Lead: *{cost_per_hot}*\n"
        f"• Running Ad: *{running_ad}*"
    )
