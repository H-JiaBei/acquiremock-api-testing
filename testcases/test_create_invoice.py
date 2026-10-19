"""创建账单接口用例：正常 / 边界 / 异常 + 字段断言。"""

import uuid

import pytest


def _full_payload(amount=25000):
    return {
        "amount": amount,
        "reference": f"REF-{uuid.uuid4().hex[:8]}",
        "webhookUrl": "https://example.com/webhook",
        "redirectUrl": "https://example.com/success",
    }


def test_create_invoice_success(api):
    """正常：合法字段返回 200，pageUrl 结构正确。"""
    resp = api.create_invoice(
        amount=25000,
        reference=f"REF-{uuid.uuid4().hex[:8]}",
        webhook_url="https://example.com/webhook",
        redirect_url="https://example.com/success",
    )
    assert resp.status_code == 200
    page = resp.json()["pageUrl"]
    assert "/checkout/" in page
    payment_id = page.rsplit("/", 1)[-1]
    assert len(payment_id) == 36  # UUID 格式


@pytest.mark.parametrize("amount", [0, -100, 1, 10**15])
def test_amount_boundary(api, amount):
    """边界：金额无下限/上限校验，0、负数、超大值均返回 200（实测发现的缺陷行为）。"""
    resp = api.session.post(
        f"{api.base_url}/api/create-invoice", json=_full_payload(amount)
    )
    assert resp.status_code == 200


@pytest.mark.parametrize("missing", ["amount", "reference", "webhookUrl", "redirectUrl"])
def test_create_invoice_missing_required(api, missing):
    """异常：缺少任一必填字段返回 422。"""
    payload = _full_payload()
    del payload[missing]
    resp = api.session.post(f"{api.base_url}/api/create-invoice", json=payload)
    assert resp.status_code == 422


@pytest.mark.parametrize("bad_amount", ["abc", 1.5])
def test_amount_wrong_type(api, bad_amount):
    """异常：amount 类型错误（字符串/浮点）返回 422。"""
    payload = _full_payload()
    payload["amount"] = bad_amount
    resp = api.session.post(f"{api.base_url}/api/create-invoice", json=payload)
    assert resp.status_code == 422


def test_duplicate_reference_allowed(api):
    """同一 reference 重复下单均返回 200（实测：接口未做唯一性约束）。"""
    ref = f"DUP-{uuid.uuid4().hex[:8]}"
    payload = _full_payload()
    payload["reference"] = ref
    r1 = api.session.post(f"{api.base_url}/api/create-invoice", json=payload)
    r2 = api.session.post(f"{api.base_url}/api/create-invoice", json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["pageUrl"] != r2.json()["pageUrl"]  # 两次生成不同 payment_id
