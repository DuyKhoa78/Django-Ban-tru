from .base import *

# ==============================================================================
# QUẢN LÝ GHI ĐÈ SETTINGS CHO MÔI TRƯỜNG DEVELOPMENT (LOCAL/TEST)
# ==============================================================================

# Trong lúc viết code thì bật DEBUG để xem lỗi
DEBUG = False

# Cho phép chạy dưới local network và localhost
ALLOWED_HOSTS = ['*']

# ── TẮT CÁC CỜ BẢO MẬT HTTPS KHI CHẠY TRÊN HTTP (LOCAL LAN) ──
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Xóa email console ra terminal (hoặc bạn có thể giữ nguyên theo base)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
