from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from core.models import LoaiTruc, GioiTinh, NhiemVuGV


# =========================================================
# 1. PHÒNG
# =========================================================
class Phong(models.Model):
    ma_phong = models.CharField(max_length=3, primary_key=True)
    loai_phong = models.IntegerField(choices=LoaiTruc.choices)
    suc_chua = models.PositiveIntegerField()
    gioi_tinh = models.IntegerField(
        choices=GioiTinh.choices,
        null=True,
        blank=True
    )
    sl_diem_danh = models.IntegerField(default=1, verbose_name="Số lượng Điểm danh")
    sl_ho_tro = models.IntegerField(default=1, verbose_name="Số lượng Hỗ trợ")

    class Meta:
        verbose_name = "Phòng"
        verbose_name_plural = "1. Danh sách phòng"
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(loai_phong=LoaiTruc.AN, gioi_tinh__isnull=True) |
                    Q(loai_phong=LoaiTruc.NGU, gioi_tinh__isnull=False)
                ),
                name="ck_phong_loai_gt"
            )
        ]

    def clean(self):
        if self.loai_phong == LoaiTruc.AN and self.gioi_tinh is not None:
            raise ValidationError("Phòng ăn không có giới tính.")
        if self.loai_phong == LoaiTruc.NGU and self.gioi_tinh is None:
            raise ValidationError("Phòng ngủ phải có giới tính.")

    def __str__(self):
        return f"{self.ma_phong}"


# =========================================================
# 2. MUA VẬT DỤNG
# =========================================================
class MuaVatDung(models.Model):

    LOAI = [
        ("CHIEU", "Chiếu"),
        ("GOI", "Gối"),
        ("VO_GOI", "Vỏ gối"),
    ]

    nam_hoc = models.CharField(max_length=10)   # 24-25
    lan_mua = models.PositiveIntegerField(default=1)
    loai_vat_dung = models.CharField(max_length=10, choices=LOAI)

    so_luong = models.PositiveIntegerField()
    ngay_mua = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('nam_hoc', 'lan_mua', 'loai_vat_dung')

    def __str__(self):
        return f"{self.get_loai_vat_dung_display()} - {self.nam_hoc} (lần {self.lan_mua})"

    @property
    def da_phan(self):
        return sum(pb.so_luong for pb in self.phan_bo.all())

    @property
    def con_lai(self):
        return self.so_luong - self.da_phan


# =========================================================
# 3. PHÂN BỔ VẬT DỤNG
# =========================================================
class PhanBoVatDung(models.Model):
    mua = models.ForeignKey(
        MuaVatDung,
        on_delete=models.CASCADE,
        related_name="phan_bo"
    )
    phong = models.ForeignKey(Phong, on_delete=models.CASCADE)
    so_luong = models.PositiveIntegerField()

    class Meta:
        unique_together = ('mua', 'phong')

    def clean(self):
        tong = sum(
            pb.so_luong
            for pb in self.mua.phan_bo.exclude(pk=self.pk)
        )

        if tong + self.so_luong > self.mua.so_luong:
            raise ValidationError("Phân bổ vượt quá số lượng đã mua!")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.phong} - {self.so_luong}"


# =========================================================
# 4. GIÁO VIÊN
# =========================================================
class GiaoVien(models.Model):
    ho_ten = models.CharField(max_length=100)
    gioi_tinh = models.IntegerField(choices=GioiTinh.choices)
    so_dien_thoai = models.CharField(max_length=15, unique=True, null=True, blank=True)
    nhiem_vu = models.IntegerField(choices=NhiemVuGV.choices, default=NhiemVuGV.DIEM_DANH)
    dang_lam = models.BooleanField(default=True)
    lich_ranh = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = "Giáo viên"
        verbose_name_plural = "3. Danh sách giáo viên"

    def __str__(self):
        return self.ho_ten


# =========================================================
# 5. HỌC SINH
# =========================================================
class HocSinh(models.Model):
    ho_ten = models.CharField(max_length=100)
    gioi_tinh = models.IntegerField(choices=GioiTinh.choices)
    lop = models.CharField(max_length=10)
    dang_hoc = models.BooleanField(default=True)

    ghi_chu = models.TextField(blank=True, null=True)

    ma_phong_an = models.ForeignKey(
        Phong,
        on_delete=models.PROTECT,
        related_name='hs_an'
    )
    ma_phong_ngu = models.ForeignKey(
        Phong,
        on_delete=models.PROTECT,
        related_name='hs_ngu'
    )

    class Meta:
        verbose_name = "Học sinh"
        verbose_name_plural = "4. Danh sách học sinh"

    def clean(self):
        # check loại phòng
        if self.ma_phong_an.loai_phong != LoaiTruc.AN:
            raise ValidationError("Phòng ăn không hợp lệ.")

        if self.ma_phong_ngu.loai_phong != LoaiTruc.NGU:
            raise ValidationError("Phòng ngủ không hợp lệ.")

        # check giới tính
        if self.ma_phong_ngu.gioi_tinh != self.gioi_tinh:
            raise ValidationError("Không đúng giới tính phòng ngủ.")

        # check sức chứa
        so_luong = HocSinh.objects.filter(
            ma_phong_ngu=self.ma_phong_ngu
        ).exclude(pk=self.pk).count()

        if so_luong >= self.ma_phong_ngu.suc_chua:
            raise ValidationError("Phòng ngủ đã đầy.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ho_ten} - {self.lop}"