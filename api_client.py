"""接口封装层：封装 AcquireMock 各接口的调用与 Webhook 签名算法。"""

import hashlib
import hmac
import json

import requests

from config import BASE_URL, TIMEOUT, WEBHOOK_SECRET


def generate_signature(payload: dict, secret: str = WEBHOOK_SECRET) -> str:
    """按被测服务的算法生成 HMAC-SHA256 签名（json 按 key 排序后签名）。"""
    message = json.dumps(payload, sort_keys=True)
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()


class AcquireMockAPI:
    """被测服务的客户端封装。"""

    def __init__(self, base_url: str = BASE_URL, secret: str = WEBHOOK_SECRET):
        self.base_url = base_url.rstrip("/")
        self.secret = secret
        self.session = requests.Session()

    # ---- 系统 ----
    def health(self) -> requests.Response:
        return self.session.get(f"{self.base_url}/health", timeout=TIMEOUT)

    # ---- 账单 ----
    def create_invoice(self, amount, reference, webhook_url, redirect_url):
        """正常创建账单（字段齐全）。"""
        return self.session.post(
            f"{self.base_url}/api/create-invoice",
            json={
                "amount": amount,
                "reference": reference,
                "webhookUrl": webhook_url,
                "redirectUrl": redirect_url,
            },
            timeout=TIMEOUT,
        )

    # ---- 收银台 ----
    def checkout(self, payment_id: str) -> requests.Response:
        return self.session.get(f"{self.base_url}/checkout/{payment_id}", timeout=TIMEOUT)

    # ---- 支付 ----
    def pay(self, payment_id, email, card_number=None, csrf_token="dummy", cookies=None):
        """发起支付（form 表单提交）。"""
        data = {"email": email, "csrf_token": csrf_token}
        if card_number:
            data.update({"card_number": card_number, "expiry": "12/30", "cvv": "123"})
        return self.session.post(
            f"{self.base_url}/api/pay/{payment_id}",
            data=data,
            cookies=cookies,
            allow_redirects=False,
            timeout=TIMEOUT,
        )

    # ---- Webhook ----
    def verify_webhook(self, payload: dict, signature: str):
        return self.session.post(
            f"{self.base_url}/webhooks/verify",
            json=payload,
            headers={"X-Signature": signature},
            timeout=TIMEOUT,
        )
