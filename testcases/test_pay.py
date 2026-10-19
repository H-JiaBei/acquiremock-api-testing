"""支付接口用例：异常、CSRF、合法卡号主流程。"""

from config import VALID_CARD, INVALID_CARD


def test_pay_payment_not_found(api):
    """异常：不存在的 payment_id 返回 404（需先通过 CSRF 校验）。"""
    resp = api.pay(
        "00000000-0000-0000-0000-000000000000",
        email="u@example.com",
        csrf_token="test-token",
        cookies={"csrf_token": "test-token"},
    )
    assert resp.status_code == 404
    assert resp.json()["error"] == "PAYMENT_NOT_FOUND"


def test_pay_csrf_mismatch(api, created_payment):
    """异常：未携带 CSRF cookie 提交支付，返回 403。"""
    resp = api.pay(
        created_payment["payment_id"],
        email="u@example.com",
        card_number=VALID_CARD,
    )
    assert resp.status_code == 403
    assert resp.json()["error"] == "CSRF_TOKEN_MISMATCH"


def test_pay_invalid_card(api, created_payment):
    """异常：非法卡号返回 402（INSUFFICIENT_FUNDS，需先通过 CSRF 校验）。"""
    resp = api.pay(
        created_payment["payment_id"],
        email="u@example.com",
        card_number=INVALID_CARD,
        csrf_token="test-token",
        cookies={"csrf_token": "test-token"},
    )
    assert resp.status_code == 402


def test_pay_valid_card_flow(api, created_payment):
    """正常主流程：合法卡号 + 正确 CSRF → 303 跳转到 OTP 页面。"""
    pid = created_payment["payment_id"]

    # 1. 先访问收银台获取 CSRF token（种在 cookie 里）
    checkout_resp = api.checkout(pid)
    assert checkout_resp.status_code == 200
    csrf = checkout_resp.cookies.get("csrf_token")
    assert csrf, "未从 checkout 获取到 csrf_token"

    # 2. 用合法卡号支付（显式携带 csrf cookie，绕过 secure cookie 在 HTTP 下不自动回传的限制）
    resp = api.session.post(
        f"{api.base_url}/api/pay/{pid}",
        data={
            "email": "user@example.com",
            "csrf_token": csrf,
            "card_number": VALID_CARD,
            "expiry": "12/30",
            "cvv": "123",
        },
        cookies={"csrf_token": csrf},
        allow_redirects=False,
    )
    assert resp.status_code == 303
    assert resp.headers["location"].endswith(f"/otp/{pid}")
