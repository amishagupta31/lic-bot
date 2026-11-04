import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

_scheduler = BackgroundScheduler(timezone='Asia/Kolkata')


def _send_daily_report():
    from bot.reports import generate_report
    from integrations.whatsapp import send_message

    report = generate_report('live')
    for key in ('CLIENT_PHONE', 'CLIENT_PHONE_2'):
        phone = os.getenv(key)
        if phone:
            try:
                send_message(phone, f"📅 *Daily Report*\n\n{report}")
            except Exception as e:
                print(f'Daily report error to {phone}: {e}')


def _send_weekly_report():
    from bot.reports import generate_report
    from integrations.whatsapp import send_message
    from integrations.sheets import get_leads_stats
    from integrations.meta_ads import get_spend_since

    stats = get_leads_stats(days=7) or {}
    spend = get_spend_since(days=7)
    total   = stats.get('total', 0)
    hot     = stats.get('hot', 0)
    spend_s = f"₹{spend:.2f}" if spend is not None else "N/A"

    text = (
        f"📊 *Weekly Report*\n\n"
        f"• Total Leads: *{total}*\n"
        f"• Hot Leads: *{hot}* 🔥\n"
        f"• Total Spend: *{spend_s}*"
    )
    for key in ('CLIENT_PHONE', 'CLIENT_PHONE_2'):
        phone = os.getenv(key)
        if phone:
            try:
                send_message(phone, text)
            except Exception as e:
                print(f'Weekly report error to {phone}: {e}')


def start_cron_jobs():
    # Daily report at 9 PM IST
    _scheduler.add_job(_send_daily_report, CronTrigger(hour=21, minute=0))
    # Weekly report every Sunday at 9 AM IST
    _scheduler.add_job(_send_weekly_report, CronTrigger(day_of_week='sun', hour=9, minute=0))

    _scheduler.start()
    print('⏰ Cron jobs started')
