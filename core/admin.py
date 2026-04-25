from django.contrib import admin
from .models import CauHinhGia


@admin.register(CauHinhGia)
class CauHinhGiaAdmin(admin.ModelAdmin):
    list_display  = ('loai_truc', 'don_gia', 'ngay_ap_dung')
    list_filter   = ('loai_truc',)
    ordering      = ('-ngay_ap_dung',)
