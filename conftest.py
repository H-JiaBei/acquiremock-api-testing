"""Pytest 全局夹具。"""

import uuid

import pytest

from api_client import AcquireMockAPI


@pytest.fixture(scope="session")
def api():
    """复用同一个客户端（内部复用 requests.Session）。"""
    return AcquireMockAPI()


@pytest.fixture()
def created_payment(api):
    """创建一个状态为 pending 的账单，返回 payment_id。"""
    resp = api.create_invoice(
        amount=25000,
        reference=f"TEST-{uuid.uuid4().hex[:8]}",
        webhook_url="https://example.com/webhook",
        redirect_url="https://example.com/success",
    )
    assert resp.status_code == 200, f"创建账单失败: {resp.text}"
    page_url = resp.json()["pageUrl"]
    payment_id = page_url.rsplit("/", 1)[-1]
    return {"payment_id": payment_id, "page_url": page_url}
