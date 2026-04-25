from django.urls import path
from . import views

urlpatterns = [
    # ── Học sinh ──
    path('admin/hocsinh/',            views.hocsinh_list,   name='admin_hocsinh'),
    path('admin/hocsinh/them/',       views.hocsinh_create, name='hocsinh_create'),
    path('admin/hocsinh/<int:pk>/sua/', views.hocsinh_edit, name='hocsinh_edit'),
    path('admin/hocsinh/<int:pk>/xoa/', views.hocsinh_delete, name='hocsinh_delete'),

    # ── Giáo viên ──
    path('admin/giaovien/',              views.giaovien_list,   name='admin_giaovien'),
    path('admin/giaovien/them/',         views.giaovien_create, name='giaovien_create'),
    path('admin/giaovien/<int:pk>/sua/', views.giaovien_edit,   name='giaovien_edit'),
    path('admin/giaovien/<int:pk>/xoa/', views.giaovien_delete, name='giaovien_delete'),

    # ── Phòng ──
    path('admin/phong/',              views.phong_list,   name='admin_phong'),
    path('admin/phong/them/',         views.phong_create, name='phong_create'),
    path('admin/phong/<str:pk>/sua/', views.phong_edit,   name='phong_edit'),

    # ── Cấu hình giá ──
    path('admin/cauhinh/', views.cauhinh_list, name='admin_cauhinh'),

    # ── Vật dụng ──
    path('admin/vatdung/', views.vatdung_list, name='admin_vatdung'),

    # ── AJAX APIs ──
    path('api/hocsinh/save/',    views.api_hocsinh_save,   name='api_hocsinh_save'),
    path('api/hocsinh/<int:pk>/delete/', views.api_hocsinh_delete, name='api_hocsinh_delete'),
    path('api/hocsinh/import/',  views.api_hocsinh_import_csv, name='api_hocsinh_import'),
    
    path('api/phong/save/',      views.api_phong_save,     name='api_phong_save'),
    path('api/phong/delete/',    views.api_phong_delete,   name='api_phong_delete'),

    path('api/giaovien/save/',   views.api_giaovien_save,  name='api_giaovien_save'),
    path('api/giaovien/<int:pk>/delete/', views.api_giaovien_delete, name='api_giaovien_delete'),
    path('api/giaovien/<int:pk>/ranh/', views.api_giaovien_ranh_save, name='api_giaovien_ranh_save'),

    path('api/cauhinh/save/',    views.api_cauhinh_save,   name='api_cauhinh_save'),
    path('api/hethong/save/',    views.api_hethong_save,   name='api_hethong_save'),

    path('api/vatdung/mua/save/', views.api_vatdung_mua_save, name='api_vatdung_mua_save'),
    path('api/vatdung/mua/delete/', views.api_vatdung_mua_delete, name='api_vatdung_mua_delete'),
    path('api/vatdung/phanbo/save/', views.api_vatdung_phanbo_save, name='api_vatdung_phanbo_save'),
    path('api/vatdung/phanbo/delete/', views.api_vatdung_phanbo_delete, name='api_vatdung_phanbo_delete'),
]
