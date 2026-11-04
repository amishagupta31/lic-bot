import os
import requests
from utils.state import get_state, set_state, next_ad_code

GRAPH = "https://graph.facebook.com/v20.0"


def _token():
    return os.getenv('META_ACCESS_TOKEN')


def _headers():
    return {"Authorization": f"Bearer {_token()}"}


def _meta_post(path, body):
    r = requests.post(f"{GRAPH}/{path}", json=body, headers=_headers())
    if not r.ok:
        err = r.json().get('error', {}).get('message', r.text)
        raise Exception(err)
    return r.json()


def _meta_get(path, params=None):
    r = requests.get(f"{GRAPH}/{path}", params=params, headers=_headers())
    if not r.ok:
        err = r.json().get('error', {}).get('message', r.text)
        raise Exception(err)
    return r.json()


def _require_ad_id(ad_code):
    ad_map = get_state('adMap') or {}
    ad_id = ad_map.get(ad_code)
    if not ad_id:
        raise Exception(f"{ad_code} ka ad ID nahi mila. .env mein META_AD_ID_{ad_code} set karo.")
    return ad_id


def _require_ad_set_id():
    ad_set_id = os.getenv('META_AD_SET_ID')
    if not ad_set_id:
        raise Exception("META_AD_SET_ID .env mein set nahi hai.")
    return ad_set_id


def pause_ad(ad_code):
    ad_id = _require_ad_id(ad_code)
    _meta_post(f"{ad_id}", {"status": "PAUSED"})


def resume_ad(ad_code):
    ad_id = _require_ad_id(ad_code)
    _meta_post(f"{ad_id}", {"status": "ACTIVE"})


def update_budget(amount_rupees):
    ad_set_id = _require_ad_set_id()
    daily_budget_paise = amount_rupees * 100
    _meta_post(f"{ad_set_id}", {"daily_budget": daily_budget_paise})


def sync_running_ad():
    ad_map = get_state('adMap') or {}
    if not ad_map:
        return

    for code, ad_id in ad_map.items():
        try:
            data = _meta_get(ad_id, params={"fields": "status"})
            if data.get('status') == 'ACTIVE':
                set_state('runningAd', code)
                print(f"✅ Running ad synced: {code}")
                return
        except Exception as e:
            print(f"syncRunningAd error for {code}: {e}")

    print("ℹ️  No active ad found at startup")


def get_spend_since(days=1):
    account_id = os.getenv('META_AD_ACCOUNT_ID')
    if not account_id:
        return None
    try:
        data = _meta_get(
            f"{account_id}/insights",
            params={"fields": "spend", "date_preset": "today" if days <= 1 else "last_7d"},
        )
        rows = data.get('data', [])
        if rows:
            return float(rows[0].get('spend', 0))
        return 0.0
    except Exception as e:
        print(f"getSpendSince error: {e}")
        return None


def get_ad_stats(ad_code):
    from integrations.sheets import get_leads_stats
    try:
        ad_id = _require_ad_id(ad_code)
        data = _meta_get(ad_id, params={"fields": "status,name"})
        status = data.get('status', 'UNKNOWN')

        spend_data = _meta_get(
            f"{ad_id}/insights",
            params={"fields": "spend,actions", "date_preset": "lifetime"},
        )
        rows = spend_data.get('data', [])
        spend = float(rows[0].get('spend', 0)) if rows else 0.0

        stats = get_leads_stats(days=90, ad_code=ad_code) or {}
        leads = stats.get('total', 0)
        hot_leads = stats.get('hot', 0)
        cost_per_hot = round(spend / hot_leads, 2) if hot_leads > 0 else None

        return {
            'status': status,
            'spend': round(spend, 2),
            'leads': leads,
            'hotLeads': hot_leads,
            'costPerHotLead': cost_per_hot,
        }
    except Exception as e:
        print(f"getAdStats error: {e}")
        return None


def get_all_ad_stats():
    ad_map = get_state('adMap') or {}
    results = {}
    for code in ad_map:
        results[code] = get_ad_stats(code)
    return results


def set_ad_id(ad_code, ad_id):
    ad_map = get_state('adMap') or {}
    ad_map[ad_code] = ad_id
    set_state('adMap', ad_map)


def create_ad(ad_code, image_url, caption):
    page_id = os.getenv('META_PAGE_ID')
    ad_account_id = os.getenv('META_AD_ACCOUNT_ID')
    display_number = os.getenv('WHATSAPP_DISPLAY_NUMBER')

    if not all([page_id, ad_account_id, display_number]):
        raise Exception("META_PAGE_ID, META_AD_ACCOUNT_ID, WHATSAPP_DISPLAY_NUMBER .env mein set nahi hain.")

    wa_link = f"https://wa.me/{display_number}?text=Hi%20{ad_code}"

    creative = _meta_post(
        f"{ad_account_id}/adcreatives",
        {
            "name": f"Bima Sakhi {ad_code}",
            "object_story_spec": {
                "page_id": page_id,
                "link_data": {
                    "image_url": image_url,
                    "message": caption,
                    "link": wa_link,
                    "call_to_action": {
                        "type": "WHATSAPP_MESSAGE",
                        "value": {"app_destination": "WHATSAPP"},
                    },
                },
            },
        },
    )
    creative_id = creative['id']

    ad_set_id = _require_ad_set_id()
    ad = _meta_post(
        f"{ad_account_id}/ads",
        {
            "name": f"Bima Sakhi {ad_code}",
            "adset_id": ad_set_id,
            "creative": {"creative_id": creative_id},
            "status": "PAUSED",
        },
    )
    return ad['id']
