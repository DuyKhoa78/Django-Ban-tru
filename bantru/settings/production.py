from .base import *

# ==============================================================================
# QUẢN LÝ GHI ĐÈ SETTINGS CHO MÔI TRƯỜNG THỰC TẾ (PRODUCTION)
# ==============================================================================

# Tắt DEBUG đi để bảo mật, nếu bị lỗi sẽ hiện trang 500 thay vì mã nguồn code
DEBUG = False

import os

# Lấy SECRET_KEY từ biến môi trường của Azure (nếu không có thì sẽ quăng lỗi)
if 'SECRET_KEY' in os.environ:
    SECRET_KEY = os.environ['SECRET_KEY']
else:
    print("Warning: Chưa cấu hình SECRET_KEY trong App Service")

# [QUAN TRỌNG] Tự động đọc Domain từ Azure (`WEBSITE_HOSTNAME`)
ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
ALLOWED_HOSTS.extend(['quanlybantru-lthg.edu.vn', '127.0.0.1'])

# Khai báo Domain tin cậy cho CSRF (để POST form / Login hoạt động)
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []

# ── BẬT TOÀN BỘ CÁC CỜ BẢO MẬT & HTTPS (BẮT BUỘC WEB CÓ CHỨNG CHỈ SSL) ──
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 năm
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Khi lên Production, Django không biết tự serve static files
# Nên phải dùng STATIC_ROOT để gm file lại cho Nginx tĩnh quản lý
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Tải biến môi trường từ file .env (rất quan trọng, đặc biệt khi dùng nền tảng cung cấp URL như Supabase/Render)
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

# Đọc kết nối dạng URL (VD: postgresql://postgres:password@db.bfrbvkiihpnvyoctmhsw.supabase.co:5432/postgres)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,  # Bắt buộc đối với Supabase
        )
    }
else:
    print("Warning: Chưa cấu hình DATABASE_URL trong hệ thống hoặc file .env")
