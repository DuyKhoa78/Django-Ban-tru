from django.urls import path
from . import views

urlpatterns = [
    path('admin/taikhoan/',           views.quan_ly_taikhoan,          name='admin_taikhoan'),
    path('api/taikhoan/',             views.api_taikhoan_list,          name='api_taikhoan_list'),
    path('api/taikhoan/save/',        views.api_taikhoan_save,         name='api_taikhoan_save'),
    path('api/taikhoan/delete/',      views.api_taikhoan_delete,       name='api_taikhoan_delete'),
    path('api/taikhoan/reset-pw/',    views.api_taikhoan_reset_password, name='api_taikhoan_reset_pw'),

    # ── Profile (cá nhân) ──
    path('profile/',                  views.profile_page,              name='profile'),
    path('api/profile/save/',         views.api_profile_save,          name='api_profile_save'),
    path('api/profile/send-otp/',     views.api_profile_send_otp,      name='api_profile_send_otp'),
    path('api/profile/verify-otp/',   views.api_profile_verify_otp,    name='api_profile_verify_otp'),
]
