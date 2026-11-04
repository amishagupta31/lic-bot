import os
import json
import requests

CLAUDE_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"

REVIEW_PROMPT = """You are reviewing a WhatsApp ad caption for LIC Bima Sakhi Yojana.
This is a legitimate LIC (Life Insurance Corporation of India) government-backed scheme for women agents.

Allowed facts:
- Stipend: ₹7,000/month year 1, ₹6,000 year 2, ₹5,000 year 3
- Registration fee: ₹860 (one time)
- Target: 24 policies per year
- For women in Karnal district
- IC-38 exam required

Review for: false income claims, misleading guarantees, prohibited financial promises.

Caption to review:
{caption}

Respond with JSON only:
{{"hasRiskyContent": bool, "warning": "string or null", "suggestion": "string or null"}}"""


def review_caption(caption):
    api_key = os.getenv('CLAUDE_API_KEY')
    if not api_key:
        return {'reviewFailed': True}

    try:
        r = requests.post(
            CLAUDE_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": MODEL,
                "max_tokens": 256,
                "messages": [
                    {"role": "user", "content": REVIEW_PROMPT.format(caption=caption)}
                ],
            },
            timeout=30,
        )
        r.raise_for_status()
        text = r.json()['content'][0]['text']
        return json.loads(text)
    except Exception as e:
        print(f"Claude review error: {e}")
        return {'reviewFailed': True}
