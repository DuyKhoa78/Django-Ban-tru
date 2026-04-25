from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone

from quanli.models import HocSinh
from nghiepvu.models import DiemDanhHS
from core.models import TrangThaiDiemDanh, GioiTinh


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'core/index.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()

        # ── Tổng học sinh đang học ──
        hs_qs = HocSinh.objects.filter(dang_hoc=True)
        total  = hs_qs.count()
        male   = hs_qs.filter(gioi_tinh=GioiTinh.NAM).count()
        female = hs_qs.filter(gioi_tinh=GioiTinh.NU).count()

        # ── Điểm danh hôm nay ──
        dd_today = DiemDanhHS.objects.filter(ngay=today)
        eating   = dd_today.filter(diem_danh_an=TrangThaiDiemDanh.CO_MAT).count()
        sleeping = dd_today.filter(diem_danh_ngu=TrangThaiDiemDanh.CO_MAT).count()
        absent_eat   = dd_today.exclude(diem_danh_an=TrangThaiDiemDanh.CO_MAT).count()
        absent_sleep = dd_today.exclude(diem_danh_ngu=TrangThaiDiemDanh.CO_MAT).count()
        absent = max(absent_eat, absent_sleep)

        # ── Chi tiết theo khối ──
        khoi_data = {}
        for khoi_prefix in ['10', '11', '12']:
            hs_khoi = hs_qs.filter(lop__startswith=khoi_prefix)
            khoi_total  = hs_khoi.count()
            khoi_male   = hs_khoi.filter(gioi_tinh=GioiTinh.NAM).count()
            khoi_female = hs_khoi.filter(gioi_tinh=GioiTinh.NU).count()

            dd_khoi       = dd_today.filter(ma_hs__lop__startswith=khoi_prefix)
            khoi_eating   = dd_khoi.filter(diem_danh_an=TrangThaiDiemDanh.CO_MAT).count()
            khoi_sleeping = dd_khoi.filter(diem_danh_ngu=TrangThaiDiemDanh.CO_MAT).count()
            khoi_phep     = dd_khoi.filter(diem_danh_an=TrangThaiDiemDanh.PHEP).count()
            khoi_vang     = dd_khoi.filter(diem_danh_an=TrangThaiDiemDanh.VANG).count()
            eat_pct   = round(khoi_eating / khoi_total * 100) if khoi_total else 0
            sleep_pct = round(khoi_sleeping / khoi_total * 100) if khoi_total else 0

            khoi_data[khoi_prefix] = {
                'total': khoi_total,
                'male':  khoi_male,
                'female': khoi_female,
                'eating': khoi_eating,
                'sleeping': khoi_sleeping,
                'phep': khoi_phep,
                'vang': khoi_vang,
                'eat_pct': eat_pct,
                'sleep_pct': sleep_pct,
            }

        ctx['stat'] = {
            'total':       total,
            'male':        male,
            'female':      female,
            'eating':      eating,
            'sleeping':    sleeping,
            'absent':      absent,
            'absent_eat':  absent_eat,
            'absent_sleep': absent_sleep,
            'khoi':        khoi_data,
        }
        ctx['khoi_list'] = [
            ('10', 'fa-school'),
            ('11', 'fa-book'),
            ('12', 'fa-graduation-cap'),
        ]
        return ctx