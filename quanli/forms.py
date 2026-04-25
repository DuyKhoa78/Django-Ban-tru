"""
quanli/forms.py – Form cho các module quản lý danh mục.
"""
from django import forms
from .models import HocSinh, GiaoVien, Phong, MuaVatDung, PhanBoVatDung
from core.models import CauHinhGia, LoaiTruc


class HocSinhForm(forms.ModelForm):
    class Meta:
        model  = HocSinh
        fields = ['ho_ten', 'gioi_tinh', 'lop', 'ma_phong_an', 'ma_phong_ngu', 'dang_hoc', 'ghi_chu']
        widgets = {
            'ho_ten':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ và tên'}),
            'gioi_tinh':   forms.Select(attrs={'class': 'form-control'}),
            'lop':         forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: 10A1'}),
            'ma_phong_an': forms.Select(attrs={'class': 'form-control'}),
            'ma_phong_ngu':forms.Select(attrs={'class': 'form-control'}),
            'ghi_chu':     forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ma_phong_an'].queryset  = Phong.objects.filter(loai_phong=LoaiTruc.AN)
        self.fields['ma_phong_ngu'].queryset = Phong.objects.filter(loai_phong=LoaiTruc.NGU)


class GiaoVienForm(forms.ModelForm):
    class Meta:
        model  = GiaoVien
        fields = ['ho_ten', 'gioi_tinh', 'so_dien_thoai', 'nhiem_vu', 'dang_lam']
        widgets = {
            'ho_ten':         forms.TextInput(attrs={'class': 'form-control'}),
            'gioi_tinh':      forms.Select(attrs={'class': 'form-control'}),
            'so_dien_thoai':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: 0901234567'}),
            'nhiem_vu':       forms.Select(attrs={'class': 'form-control'}),
        }


class PhongForm(forms.ModelForm):
    class Meta:
        model  = Phong
        fields = ['ma_phong', 'loai_phong', 'suc_chua', 'gioi_tinh', 'sl_diem_danh', 'sl_ho_tro']
        widgets = {
            'ma_phong':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: HT.A'}),
            'loai_phong':forms.Select(attrs={'class': 'form-control'}),
            'suc_chua':  forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'gioi_tinh': forms.Select(attrs={'class': 'form-control'}),
            'sl_diem_danh': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'sl_ho_tro': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class CauHinhGiaForm(forms.ModelForm):
    class Meta:
        model  = CauHinhGia
        fields = ['loai_truc', 'don_gia', 'ngay_ap_dung']
        widgets = {
            'loai_truc':    forms.Select(attrs={'class': 'form-control'}),
            'don_gia':      forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '1000'}),
            'ngay_ap_dung': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class MuaVatDungForm(forms.ModelForm):
    class Meta:
        model  = MuaVatDung
        fields = ['nam_hoc', 'lan_mua', 'loai_vat_dung', 'so_luong']
        widgets = {
            'nam_hoc':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: 24-25'}),
            'lan_mua':       forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'loai_vat_dung': forms.Select(attrs={'class': 'form-control'}),
            'so_luong':      forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class PhanBoVatDungForm(forms.ModelForm):
    class Meta:
        model  = PhanBoVatDung
        fields = ['mua', 'phong', 'so_luong']
        widgets = {
            'mua':      forms.Select(attrs={'class': 'form-control'}),
            'phong':    forms.Select(attrs={'class': 'form-control'}),
            'so_luong': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Chỉ cho phân bổ vào phòng ngủ
        self.fields['phong'].queryset = Phong.objects.filter(loai_phong=LoaiTruc.NGU)
