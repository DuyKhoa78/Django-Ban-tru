from django.contrib import admin
from .models import HocSinh, GiaoVien, Phong, MuaVatDung, PhanBoVatDung


@admin.register(Phong)
class PhongAdmin(admin.ModelAdmin):
    list_display  = ('ma_phong', 'loai_phong', 'suc_chua', 'gioi_tinh')
    list_filter   = ('loai_phong', 'gioi_tinh')
    search_fields = ('ma_phong',)


@admin.register(HocSinh)
class HocSinhAdmin(admin.ModelAdmin):
    list_display  = ('ho_ten', 'lop', 'gioi_tinh', 'ma_phong_an', 'ma_phong_ngu', 'dang_hoc')
    list_filter   = ('lop', 'gioi_tinh', 'dang_hoc', 'ma_phong_an')
    search_fields = ('ho_ten', 'lop')
    list_editable = ('dang_hoc',)
    ordering      = ('lop', 'ho_ten')


@admin.register(GiaoVien)
class GiaoVienAdmin(admin.ModelAdmin):
    list_display  = ('ho_ten', 'gioi_tinh', 'so_dien_thoai', 'dang_lam')
    list_filter   = ('gioi_tinh', 'dang_lam')
    search_fields = ('ho_ten',)
    list_editable = ('dang_lam',)


@admin.register(MuaVatDung)
class MuaVatDungAdmin(admin.ModelAdmin):
    list_display = ('nam_hoc', 'lan_mua', 'loai_vat_dung', 'so_luong', 'ngay_mua')
    list_filter  = ('nam_hoc', 'loai_vat_dung')


@admin.register(PhanBoVatDung)
class PhanBoVatDungAdmin(admin.ModelAdmin):
    list_display = ('mua', 'phong', 'so_luong')
    list_filter  = ('phong',)
