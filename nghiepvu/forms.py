"""
nghiepvu/forms.py – Form cho điểm danh & phân công GV.
"""
from django import forms
from .models import DiemDanhHS, DiemDanhPhong, PhanCongTrucGV
from quanli.models import GiaoVien, Phong
from core.models import LoaiTruc


class PhanCongTrucGVForm(forms.ModelForm):
    class Meta:
        model  = PhanCongTrucGV
        fields = ['ma_gv', 'ma_phong', 'ngay', 'loai_truc', 'ma_gv_truc_thay', 'xac_nhan_truc']
        widgets = {
            'ma_gv':          forms.Select(attrs={'class': 'form-control'}),
            'ma_phong':       forms.Select(attrs={'class': 'form-control'}),
            'ngay':           forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'loai_truc':      forms.Select(attrs={'class': 'form-control'}),
            'ma_gv_truc_thay':forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ma_gv'].queryset          = GiaoVien.objects.filter(dang_lam=True).order_by('ho_ten')
        self.fields['ma_gv_truc_thay'].queryset = GiaoVien.objects.filter(dang_lam=True).order_by('ho_ten')
        self.fields['ma_gv_truc_thay'].required = False
