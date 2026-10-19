"""收银台页面接口用例。"""


def test_checkout_valid(api, created_payment):
    """正常：pending 状态的账单返回 200 的 HTML 收银台页面。"""
    resp = api.checkout(created_payment["payment_id"])
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


def test_checkout_not_found(api):
    """异常：不存在的 payment_id 返回 404，错误码为 PAYMENT_NOT_FOUND。"""
    resp = api.checkout("00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
    assert resp.json()["error"] == "PAYMENT_NOT_FOUND"
