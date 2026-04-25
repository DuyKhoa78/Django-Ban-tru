from django.db import models
from core.models import LoaiTruc, TrangThaiDiemDanh
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q, F
from quanli.models import HocSinh, GiaoVien, Phong
# Create your models here.



class DiemDanhPhong(models.Model):
    ma_phong = models.ForeignKey(
        Phong,
        on_delete=models.CASCADE,
        related_name="ds_diem_danh"
    )

    ngay = models.DateField(default=timezone.now)

    loai_truc = models.IntegerField(
        choices=LoaiTruc.choices
    )

    da_diem_danh = models.BooleanField(default=False)

    thoi_gian = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Điểm danh phòng"
        verbose_name_plural = "Điểm danh theo phòng"
        constraints = [
            models.UniqueConstraint(
                fields=['ma_phong', 'ngay', 'loai_truc'],
                name='UQ_Phong_Ngay_Loai'
            )
        ]

    def __str__(self):
        return f"{self.ma_phong} - {self.ngay} - {self.get_loai_truc_display()}"


class DiemDanhHS(models.Model):
    ma_hs = models.ForeignKey(HocSinh, on_delete=models.CASCADE, verbose_name="Học sinh")
    ngay = models.DateField(default=timezone.now, verbose_name="Ngày")
    diem_danh_an = models.IntegerField(
        choices=TrangThaiDiemDanh.choices, default=TrangThaiDiemDanh.CO_MAT, verbose_name="Điểm danh ăn"
    )
    diem_danh_ngu = models.IntegerField(
        choices=TrangThaiDiemDanh.choices, default=TrangThaiDiemDanh.CO_MAT, verbose_name="Điểm danh ngủ"
    )
    ghi_chu = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ghi chú")

    class Meta:
        verbose_name = "Điểm danh"
        verbose_name_plural = "5. Điểm danh học sinh"
        constraints = [
            models.UniqueConstraint(fields=['ma_hs', 'ngay'], name='UQ_DiemDanh_Ngay')
        ]
        indexes = [models.Index(fields=['ngay'])]

    def __str__(self):
        return f"{self.ma_hs.ho_ten} | {self.ngay}"


# =========================================================
# 6. Bảng Phân công trực GV
# =========================================================
class PhanCongTrucGV(models.Model):
    ma_gv = models.ForeignKey(
        GiaoVien, on_delete=models.CASCADE, related_name='ds_phan_cong', verbose_name="GV phân công"
    )
    ma_gv_truc_thay = models.ForeignKey(
        GiaoVien, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='ds_truc_thay', verbose_name="GV trực thay"
    )
    ma_phong = models.ForeignKey(Phong, on_delete=models.CASCADE, verbose_name="Phòng")
    ngay = models.DateField(verbose_name="Ngày trực")
    loai_truc = models.IntegerField(choices=LoaiTruc.choices, verbose_name="Loại ca")
    xac_nhan_truc = models.BooleanField(default=True, verbose_name="Xác nhận trực")

    class Meta:
        verbose_name = "Phân công"
        verbose_name_plural = "6. Phân công trực GV"
        constraints = [
            # Chặn tự trực thay cho chính mình
            models.CheckConstraint(check=~Q(ma_gv=F('ma_gv_truc_thay')), name='CK_Khong_Tu_Thay'),
            # Chặn 1 GV trực 2 phòng cùng loại (cùng ngày, cùng loại ca Ăn hoặc Ngủ)
            # Không chặn GV vừa trực Ăn vừa trực Ngủ (2 ca khác thời gian)
            models.UniqueConstraint(
                fields=['ma_gv', 'ngay', 'loai_truc', 'ma_phong'],
                name='UQ_Lich_GV_Ngay_Loai_Phong'
            ),
        ]
        # LƯU Ý: Đã xóa UQ_Lich_Ca_Nhan_GV – GV có thể trực cả phòng Ăn lẫn phòng Ngủ cùng ngày.

    def clean(self):
        if self.ma_gv == self.ma_gv_truc_thay:
            raise ValidationError("Giáo viên không thể tự trực thay cho chính mình.")
        
        # Đảm bảo loại phòng khớp với loại trực (Ăn trực ở phòng Ăn)
        if self.ma_phong.loai_phong != self.loai_truc:
            raise ValidationError(f"Phòng {self.ma_phong.ma_phong} không phù hợp với ca trực này.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

# =========================================================
# 7. Lịch Khung (Phân công cố định T2-T6)
# =========================================================
class ThuTrongTuan(models.IntegerChoices):
    THU_2 = 0, "Thứ 2"
    THU_3 = 1, "Thứ 3"
    THU_4 = 2, "Thứ 4"
    THU_5 = 3, "Thứ 5"
    THU_6 = 4, "Thứ 6"

class LichTrucCoDinh(models.Model):
    ma_phong = models.ForeignKey(Phong, on_delete=models.CASCADE, verbose_name="Phòng")
    ma_gv = models.ForeignKey(GiaoVien, on_delete=models.CASCADE, verbose_name="Giáo viên")
    thu = models.IntegerField(choices=ThuTrongTuan.choices, verbose_name="Thứ trong tuần")
    
    class Meta:
        verbose_name = "Lịch trực cố định"
        verbose_name_plural = "7. Lịch trực khung"
        constraints = [
            # GV có thể vừa trực phòng Ăn vừa trực phòng Ngủ cùng ngày
            # nhưng không được trực 2 phòng cùng loại (2 phòng ăn hoặc 2 phòng ngủ)
            models.UniqueConstraint(fields=['ma_gv', 'thu', 'ma_phong'], name='UQ_LichCoDinh_GV_Thu_Phong')
        ]

    def __str__(self):
        return f"{self.ma_phong} | {self.get_thu_display()} | {self.ma_gv}"

