import requests
from django.conf import settings


def trigger_stk_push(user_id: int, amount: str, purpose: str):
    url = f"{settings.LIPANA_BASE_URL}/api/transactions/push-stk"
    headers = {
        'Authorization': f"Bearer {settings.LIPANA_API_KEY}",
        'Content-Type': 'application/json',
    }
    payload = {
        'user_id': user_id,
        'amount': str(amount),
        'purpose': purpose,
        'callback_url': '/api/payments/lipana/callback',
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.json()