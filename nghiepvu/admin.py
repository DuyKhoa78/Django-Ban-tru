from django.contrib import admin
from .models import DiemDanhHS, DiemDanhPhong, PhanCongTrucGV


@admin.register(DiemDanhHS)
class DiemDanhHSAdmin(admin.ModelAdmin):
    list_display  = ('ma_hs', 'ngay', 'diem_danh_an', 'diem_danh_ngu', 'ghi_chu')
    list_filter   = ('ngay', 'diem_danh_an', 'diem_danh_ngu')
    search_fields = ('ma_hs__ho_ten', 'ma_hs__lop')
    date_hierarchy = 'ngay'
    ordering      = ('-ngay', 'ma_hs__lop', 'ma_hs__ho_ten')


@admin.register(DiemDanhPhong)
class DiemDanhPhongAdmin(admin.ModelAdmin):
    list_display  = ('ma_phong', 'ngay', 'loai_truc', 'da_diem_danh')
    list_filter   = ('loai_truc', 'da_diem_danh', 'ngay')
    date_hierarchy = 'ngay'


@admin.register(PhanCongTrucGV)
class PhanCongTrucGVAdmin(admin.ModelAdmin):
    list_display  = ('ma_gv', 'ma_phong', 'ngay', 'loai_truc', 'ma_gv_truc_thay', 'xac_nhan_truc')
    list_filter   = ('loai_truc', 'xac_nhan_truc', 'ngay')
    search_fields = ('ma_gv__ho_ten', 'ma_phong__ma_phong')
    date_hierarchy = 'ngay'
    ordering      = ('-ngay', 'loai_truc')
