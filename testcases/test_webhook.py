"""Webhook 验签接口用例。"""

from api_client import generate_signature


def test_webhook_valid_signature(api):
    """正常：正确签名返回 200 且 valid=true。"""
    payload = {"payment_id": "pay_1", "status": "paid", "amount": 100}
    sig = generate_signature(payload)
    resp = api.verify_webhook(payload, sig)
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


def test_webhook_wrong_signature(api):
    """异常：错误签名返回 200 但 valid=false（验签逻辑不抛错，只返回结果）。"""
    payload = {"payment_id": "pay_1", "status": "paid"}
    resp = api.verify_webhook(payload, "deadbeef" * 8)
    assert resp.status_code == 200
    assert resp.json()["valid"] is False


def test_webhook_missing_signature(api):
    """异常：缺少 X-Signature 请求头返回 400。"""
    resp = api.session.post(
        f"{api.base_url}/webhooks/verify", json={"payment_id": "pay_1"}
    )
    assert resp.status_code == 400
