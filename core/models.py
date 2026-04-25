from django.db import models
from django.conf import settings
from django.utils import timezone


class GioiTinh(models.IntegerChoices):
    NAM = 0, "Nam"
    NU = 1, "Nữ"

class NhiemVuGV(models.IntegerChoices):
    DIEM_DANH = 0, "Điểm danh"
    HO_TRO = 1, "Hỗ trợ"

class LoaiTruc(models.IntegerChoices):
    AN = 0, "Ăn"
    NGU = 1, "Ngủ"

class TrangThaiDiemDanh(models.IntegerChoices):
    CO_MAT = 0, "Có mặt"
    VANG   = 1, "Vắng"
    PHEP   = 2, "Phép"

class CauHinhGia(models.Model):
    loai_truc = models.IntegerField(choices=LoaiTruc.choices, verbose_name="Loại trực")
    don_gia = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Đơn giá")
    ngay_ap_dung = models.DateField(default=timezone.now, verbose_name="Ngày áp dụng")
    nguoi_cap_nhat = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Người chỉnh sửa",
        related_name='cauhinh_da_sua',
    )

    class Meta:
        verbose_name = "Cấu hình giá"
        verbose_name_plural = "2. Cấu hình giá"
        unique_together = ('loai_truc', 'ngay_ap_dung')

    def __str__(self):
        return f"{self.get_loai_truc_display()} | {self.ngay_ap_dung} | {self.don_gia:,}đ"


class CauHinhHeThong(models.Model):
    """Singleton – chỉ 1 bản ghi (pk=1). Lưu cấu hình chung của hệ thống."""
    nam_hoc = models.CharField(
        max_length=20, default="2025-2026",
        verbose_name="Năm học"
    )
    nguoi_phu_trach = models.CharField(
        max_length=100, default="Tạ Thị Diệu Lê",
        verbose_name="Người phụ trách bán trú"
    )
    ten_truong = models.CharField(
        max_length=200, default="LÊ THỊ HỒNG GẤM",
        verbose_name="Tên trường/trung tâm"
    )
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cấu hình hệ thống"
        verbose_name_plural = "1. Cấu hình hệ thống"

    def __str__(self):
        return f"Cấu hình – NH {self.nam_hoc}"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
