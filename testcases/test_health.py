"""系统健康检查接口用例。"""


def test_health_ok(api):
    """正常：/health 返回 200，且核心字段类型与取值正确。"""
    resp = api.health()
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["version"] == "2.0.0"
    assert data["currency"] == "USD"
    assert isinstance(data["timestamp"], str)
