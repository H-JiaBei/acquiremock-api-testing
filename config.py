"""配置层：被测服务地址、测试常量。"""

# 被测服务地址（AcquireMock 本地部署）
BASE_URL = "http://127.0.0.1:8000"

# 与 acquiremock/.env 中 WEBHOOK_SECRET 保持一致（本地 mock，测试专用）
WEBHOOK_SECRET = "dev-only-secret-key-0123456789abcdef-0123456789abcdef"

# 测试卡号（AcquireMock 只认这一张卡为合法卡）
VALID_CARD = "4444444444444444"
INVALID_CARD = "1111111111111111"

# 请求超时（秒）
TIMEOUT = 10
