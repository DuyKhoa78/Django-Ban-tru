from django.urls import path
from . import views

urlpatterns = [
    # ── Điểm danh ──
    path('diemdanh/an/',  views.diemdanh_an,  name='diemdanh_an'),
    path('diemdanh/ngu/', views.diemdanh_ngu, name='diemdanh_ngu'),

    # ── API điểm danh (cho JS fetch) ──
    path('api/phong/<str:loai>/',     views.api_phong_list,    name='api_phong_list'),
    path('api/hocsinh/<str:loai>/',   views.api_hocsinh_list,  name='api_hocsinh_list'),
    path('api/diemdanh/',             views.api_diemdanh_get,  name='api_diemdanh_get'),
    path('api/diemdanh/save/',        views.api_diemdanh_save, name='api_diemdanh_save'),

    path('api/lichtruc/save/',        views.api_lichtruc_save,   name='api_lichtruc_save'),
    path('api/lichtruc/delete/',      views.api_lichtruc_delete, name='api_lichtruc_delete'),

    # ── Lịch trực ──
    path('lichtruc/',                 views.lichtruc,       name='lichtruc'),
    path('admin/lichtruc/',           views.phan_cong_truc, name='admin_lichtruc'),
    path('admin/lichtruc/<int:pk>/xoa/', views.phan_cong_xoa, name='phan_cong_xoa'),
    path('admin/lichtruc_khung/',     views.phan_cong_khung, name='admin_lichtruc_khung'),
    path('api/lichtruc_khung/auto/',  views.api_lichtruc_khung_auto, name='api_lichtruc_khung_auto'),
    path('api/lichtruc_khung/save/',  views.api_lichtruc_khung_save, name='api_lichtruc_khung_save'),
    path('api/lichtruc_khung/apply/', views.api_lichtruc_khung_apply, name='api_lichtruc_khung_apply'),
    path('api/lichtruc/apply-khung/', views.api_apply_khung_to_week, name='api_apply_khung_to_week'),
    path('api/lichtruc/week/',        views.api_lichtruc_week,       name='api_lichtruc_week'),
    path('api/lichtruc/week-public/', views.api_lichtruc_week_public, name='api_lichtruc_week_public'),
    path('api/lichtruc/month/',       views.api_lichtruc_month,      name='api_lichtruc_month'),
    path('api/lichtruc/export/',      views.api_export_lich_gv,      name='api_export_lich_gv'),

    # ── Báo cáo ──
    path('baocao/',                   views.baocao,                name='baocao'),
    path('api/baocao/diemdanh/',      views.api_baocao_diemdanh,   name='api_baocao_diemdanh'),
    path('api/baocao/full/',           views.api_baocao_full,       name='api_baocao_full'),
    path('api/baocao/luong-gv/',      views.api_baocao_luong_gv,   name='api_baocao_luong_gv'),
]
