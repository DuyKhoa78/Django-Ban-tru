from django.db import models
from django.contrib.auth.models import AbstractUser


class StaffUser(AbstractUser):
    ROLE_ADMIN   = 'admin'
    ROLE_HOC_VU  = 'hoc_vu'
    ROLE_QUAN_LY = 'quan_ly'
    ROLE_KE_TOAN = 'ke_toan'

    ROLE_CHOICES = [
        (ROLE_ADMIN,   'Admin'),
        (ROLE_HOC_VU,  'Học vụ'),
        (ROLE_QUAN_LY, 'Quản lý'),
        (ROLE_KE_TOAN, 'Kế toán'),
    ]

    fullname = models.CharField(default='', max_length=100, verbose_name='Họ và tên')
    position = models.CharField(default='', max_length=100, verbose_name='Chức vụ', blank=True)
    role     = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_KE_TOAN,
        verbose_name='Vai trò',
    )

    class Meta:
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Quản lý người dùng'

    def __str__(self):
        return f"{self.fullname or self.username} ({self.get_role_display()})"

    # ----- Helper properties -----
    @property
    def is_admin(self):
        """Superuser hoặc role='admin' đều được coi là Admin."""
        return self.is_superuser or self.role == self.ROLE_ADMIN

    @property
    def is_hoc_vu(self):
        return self.role == self.ROLE_HOC_VU

    @property
    def is_quan_ly(self):
        return self.role == self.ROLE_QUAN_LY

    @property
    def is_ke_toan(self):
        return self.role == self.ROLE_KE_TOAN

    @property
    def can_diem_danh(self):
        """Admin + Học vụ được điểm danh & xuất file"""
        return self.is_admin or self.is_hoc_vu

    @property
    def can_quan_ly_danh_muc(self):
        """Admin + Quản lý được chỉnh giá, vật dụng, phân công trực"""
        return self.is_admin or self.is_quan_ly

    @property
    def can_quan_tri(self):
        """Chỉ Admin được thêm/sửa/xóa HS, GV, xếp phòng"""
        return self.is_admin