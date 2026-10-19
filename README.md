# AcquireMock 接口自动化测试工程

针对本地部署的支付网关模拟器 [AcquireMock](https://github.com/ashfromsky/acquiremock) 的接口自动化测试。

## 技术栈

- Python 3.12 + requests + Pytest + pytest-html

## 目录结构（分层设计）

```
acquiremock-tests/
├── config.py            # 配置层：服务地址、测试常量
├── api_client.py        # 接口封装层：封装接口调用 + Webhook 签名算法
├── conftest.py          # 夹具层：session 客户端、账单 fixture
├── pytest.ini           # pytest 配置（自动生成 HTML 报告）
└── testcases/           # 用例层
    ├── test_health.py            # 健康检查
    ├── test_create_invoice.py    # 创建账单（正常/边界/异常）
    ├── test_webhook.py           # Webhook 验签
    ├── test_checkout.py          # 收银台页面
    └── test_pay.py               # 支付（CSRF/非法卡/主流程）
```

## 运行方式

```bash
# 1. 先启动被测服务（在 acquiremock 目录）
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 2. 安装测试依赖
pip install -r requirements.txt

# 3. 运行测试（自动生成 reports/report.html）
pytest
```

## 用例覆盖

| 维度 | 覆盖点 |
|---|---|
| 正常 | 健康检查、创建账单、收银台、合法卡号支付主流程、Webhook 验签 |
| 异常 | 缺必填字段、类型错误、非法卡号、CSRF 缺失、签名缺失/错误、账单不存在 |
| 边界 | 金额 0 / 负数 / 超大值 |

## 实测发现的缺陷（被测服务）

1. **金额无边界校验**：amount=0、负数、超大值均返回 200（应做下限/上限校验）。
2. **reference 无唯一性约束**：同一 reference 可重复创建账单（与「幂等」设计不符）。
3. **文档与实现不一致**：README 的启动命令、接口路径与真实代码不符。

## 许可证

本项目为个人测试工程，与被测服务（AcquireMock，Apache-2.0）相互独立。
