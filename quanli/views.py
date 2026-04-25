"""
quanli/views.py – Views quản lý danh mục.

Quyền:
  - Admin only    : HocSinh CRUD, GiaoVien CRUD, Phong CRUD
  - Admin + QuanLy: CauHinhGia, MuaVatDung, PhanBoVatDung, PhanCongTrucGV
"""
import json
import csv
import io
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from .models import HocSinh, GiaoVien, Phong, MuaVatDung, PhanBoVatDung
from core.models import CauHinhGia, CauHinhHeThong, LoaiTruc
from accounts.models import StaffUser
from .forms import (
    HocSinhForm, GiaoVienForm, PhongForm,
    CauHinhGiaForm, MuaVatDungForm, PhanBoVatDungForm,
)


# ─────────────────────────────────────────────────────────
# HỌC SINH
# ─────────────────────────────────────────────────────────
@role_required('admin', 'quan_ly')
def hocsinh_list(request):
    # Lấy TẤT CẢ học sinh để JS có thể filter đủ loại, sắp xếp theo Mã BT (id)
    qs_all = HocSinh.objects.all().select_related('ma_phong_an', 'ma_phong_ngu').order_by('id')

    # Serialize toàn bộ HS cho JS (filter client-side)
    hs_json = json.dumps([{
        'id': hs.pk,
        'ho_ten': hs.ho_ten,
        'gioi_tinh': hs.gioi_tinh,
        'lop': hs.lop,
        'phong_an': hs.ma_phong_an.ma_phong if hs.ma_phong_an_id else '',
        'phong_ngu': hs.ma_phong_ngu.ma_phong if hs.ma_phong_ngu_id else '',
        'dang_hoc': hs.dang_hoc,
        'ghi_chu': hs.ghi_chu or ''
    } for hs in qs_all])

    ds_lop = HocSinh.objects.values_list('lop', flat=True).distinct().order_by('lop')
    ds_phong = Phong.objects.all().order_by('loai_phong', 'ma_phong')
    return render(request, 'quanli/hocsinh.html', {
        'hs_json': hs_json,
        'ds_lop': ds_lop,
        'ds_phong': ds_phong,
        'active': 'admin_hocsinh',
    })


@role_required('admin')
def hocsinh_create(request):
    form = HocSinhForm(request.POST or None)
    if form.is_valid():
        try:
            hs = form.save()
            messages.success(request, f'Đã thêm học sinh {hs.ho_ten}.')
            return redirect('admin_hocsinh')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'quanli/forms/hocsinh_form.html', {'form': form, 'action': 'Thêm mới'})


@role_required('admin')
def hocsinh_edit(request, pk):
    hs   = get_object_or_404(HocSinh, pk=pk)
    form = HocSinhForm(request.POST or None, instance=hs)
    if form.is_valid():
        try:
            form.save()
            messages.success(request, f'Đã cập nhật {hs.ho_ten}.')
            return redirect('admin_hocsinh')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'quanli/forms/hocsinh_form.html', {'form': form, 'action': 'Chỉnh sửa', 'obj': hs})


@role_required('admin')
def hocsinh_delete(request, pk):
    hs = get_object_or_404(HocSinh, pk=pk)
    if request.method == 'POST':
        hs.dang_hoc = False
        hs.save()
        messages.success(request, f'Đã ẩn học sinh {hs.ho_ten}.')
        return redirect('admin_hocsinh')
    return render(request, 'core/confirm_delete.html', {'obj': hs, 'ten': hs.ho_ten})


# ─────────────────────────────────────────────────────────
# GIÁO VIÊN
# ─────────────────────────────────────────────────────────
@role_required('admin', 'quan_ly')
def giaovien_list(request):
    q  = request.GET.get('q', '').strip()
    
    from django.db.models import Count, Q
    from datetime import date
    today = date.today()
    
    qs = GiaoVien.objects.filter(dang_lam=True).annotate(
        ca_thang_count=Count('ds_phan_cong', filter=Q(ds_phan_cong__ngay__month=today.month, ds_phan_cong__ngay__year=today.year))
    )
    if q:
        qs = qs.filter(ho_ten__icontains=q)
    qs = qs.order_by('ho_ten')

    gv_data = []
    for gv in qs:
        gv_data.append({
            'id': gv.pk,
            'ho_ten': gv.ho_ten,
            'gioi_tinh': gv.gioi_tinh,
            'nhiem_vu': getattr(gv, 'nhiem_vu', 0),
            'so_dien_thoai': gv.so_dien_thoai or '',
            'dang_lam': gv.dang_lam,
            'ca_thang': getattr(gv, 'ca_thang_count', 0),
            'lich_ranh': gv.lich_ranh if isinstance(gv.lich_ranh, list) and len(gv.lich_ranh) == 5 else [False]*5 
        })

    paginator = Paginator(qs, 30)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'quanli/giaovien.html', {
        'page_obj': page_obj, 
        'q': q, 
        'gv_json': json.dumps(gv_data),
        'active': 'admin_giaovien'
    })


@role_required('admin')
def giaovien_create(request):
    form = GiaoVienForm(request.POST or None)
    if form.is_valid():
        gv = form.save()
        messages.success(request, f'Đã thêm giáo viên {gv.ho_ten}.')
        return redirect('admin_giaovien')
    return render(request, 'quanli/forms/giaovien_form.html', {'form': form, 'action': 'Thêm mới'})


@role_required('admin')
def giaovien_edit(request, pk):
    gv   = get_object_or_404(GiaoVien, pk=pk)
    form = GiaoVienForm(request.POST or None, instance=gv)
    if form.is_valid():
        form.save()
        messages.success(request, f'Đã cập nhật {gv.ho_ten}.')
        return redirect('admin_giaovien')
    return render(request, 'quanli/forms/giaovien_form.html', {'form': form, 'action': 'Chỉnh sửa', 'obj': gv})


@role_required('admin')
def giaovien_delete(request, pk):
    gv = get_object_or_404(GiaoVien, pk=pk)
    if request.method == 'POST':
        gv.dang_lam = False
        gv.save()
        messages.success(request, f'Đã ẩn giáo viên {gv.ho_ten}.')
        return redirect('admin_giaovien')
    return render(request, 'core/confirm_delete.html', {'obj': gv, 'ten': gv.ho_ten})


# ─────────────────────────────────────────────────────────
# PHÒNG
# ─────────────────────────────────────────────────────────
@role_required('admin', 'quan_ly')
def phong_list(request):
    ds_phong = Phong.objects.annotate(
        hs_count_an=Count('hs_an', filter=Q(hs_an__dang_hoc=True), distinct=True),
        hs_count_ngu=Count('hs_ngu', filter=Q(hs_ngu__dang_hoc=True), distinct=True)
    ).order_by('loai_phong', 'ma_phong')
    
    # Chuẩn bị data cho JS
    phong_data = []
    for p in ds_phong:
        count = p.hs_count_an if p.loai_phong == 0 else p.hs_count_ngu
        phong_data.append({
            'ma_phong': p.ma_phong,
            'loai_phong': p.loai_phong,
            'suc_chua': p.suc_chua,
            'gioi_tinh': p.gioi_tinh,
            'sl_diem_danh': getattr(p, 'sl_diem_danh', 1),
            'sl_ho_tro': getattr(p, 'sl_ho_tro', 1),
            'hs_count': count
        })

    return render(request, 'quanli/phong.html', {
        'ds_phong': ds_phong,
        'phong_json': json.dumps(phong_data),
        'active': 'admin_phong'
    })


@role_required('admin')
def phong_create(request):
    form = PhongForm(request.POST or None)
    if form.is_valid():
        try:
            ph = form.save()
            messages.success(request, f'Đã thêm phòng {ph.ma_phong}.')
            return redirect('admin_phong')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'quanli/forms/phong_form.html', {'form': form, 'action': 'Thêm mới'})


@role_required('admin')
def phong_edit(request, pk):
    ph   = get_object_or_404(Phong, ma_phong=pk)
    form = PhongForm(request.POST or None, instance=ph)
    if form.is_valid():
        try:
            form.save()
            messages.success(request, f'Đã cập nhật phòng {ph.ma_phong}.')
            return redirect('admin_phong')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'quanli/forms/phong_form.html', {'form': form, 'action': 'Chỉnh sửa', 'obj': ph})


# ─────────────────────────────────────────────────────────
# CẤU HÌNH GIÁ & VẬT DỤNG  (Admin + Quản lý)
# ─────────────────────────────────────────────────────────
@role_required('admin', 'quan_ly', 'ke_toan')
def cauhinh_list(request):
    ds = CauHinhGia.objects.select_related('nguoi_cap_nhat').all().order_by('-ngay_ap_dung')
    form = CauHinhGiaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Đã lưu cấu hình giá.')
        return redirect('admin_cauhinh')

    # Lấy đơn giá hiện tại
    gia_an = CauHinhGia.objects.filter(loai_truc=LoaiTruc.AN).order_by('-ngay_ap_dung').first()
    gia_ngu = CauHinhGia.objects.filter(loai_truc=LoaiTruc.NGU).order_by('-ngay_ap_dung').first()

    hethong = CauHinhHeThong.get()
    # Danh sách user có thể làm phụ trách (quan_ly + admin)
    quan_ly_users = StaffUser.objects.filter(
        role__in=['quan_ly', 'admin'], is_active=True
    ).order_by('fullname')

    return render(request, 'quanli/cauhinh.html', {
        'ds': ds,
        'form': form,
        'active': 'admin_cauhinh',
        'curr_an': gia_an.don_gia if gia_an else 0,
        'curr_ngu': gia_ngu.don_gia if gia_ngu else 0,
        'last_updated': ds[0].ngay_ap_dung if ds.exists() else None,
        'hethong': hethong,
        'quan_ly_users': quan_ly_users,
    })


@role_required('admin', 'quan_ly', 'ke_toan')
def vatdung_list(request):
    mua_recs = MuaVatDung.objects.all().prefetch_related('phan_bo', 'phan_bo__phong').order_by('-ngay_mua')
    
    mua_data = []
    for m in mua_recs:
        mua_data.append({
            'id': m.pk,
            'nam_hoc': m.nam_hoc,
            'lan_mua': m.lan_mua,
            'loai': m.loai_vat_dung,
            'so_luong': m.so_luong,
            'ngay_mua': m.ngay_mua.isoformat()
        })
    
    phanbo_data = []
    for m in mua_recs:
        for pb in m.phan_bo.all():
            phanbo_data.append({
                'id': pb.pk,
                'mua_id': m.pk,
                'phong': pb.phong.ma_phong,
                'so_luong': pb.so_luong
            })

    ds_phong = Phong.objects.filter(loai_phong=LoaiTruc.NGU).order_by('ma_phong')
    
    return render(request, 'quanli/vatdung.html', {
        'active': 'admin_vatdung',
        'mua_json': json.dumps(mua_data),
        'phanbo_json': json.dumps(phanbo_data),
        'ds_phong': ds_phong
    })


# ─────────────────────────────────────────────────────────
# AJAX APIs
# ─────────────────────────────────────────────────────────

@require_POST
@role_required('admin')
def api_hocsinh_save(request):
    try:
        data        = json.loads(request.body)
        editing_id  = data.get('id')
        ho_ten      = str(data.get('ho_ten', '')).strip()
        lop         = str(data.get('lop', '')).strip().upper()
        gioi_tinh   = data.get('gioi_tinh')
        ma_phong_an = str(data.get('ma_phong_an', '')).strip().upper()
        ma_phong_ngu= str(data.get('ma_phong_ngu', '')).strip().upper()
        dang_hoc    = data.get('dang_hoc')
        # Xử lý dang_hoc: chuẩn hóa sang bool (False phải được giữ nguyên)
        if dang_hoc is None:
            dang_hoc = True
        else:
            dang_hoc = bool(dang_hoc)
        ghi_chu     = str(data.get('ghi_chu', '')).strip()

        errors = {}
        if not ho_ten:   errors['ho_ten']      = 'Họ tên không được để trống'
        if not lop:      errors['lop']          = 'Lớp không được để trống'
        if gioi_tinh is None: errors['gioi_tinh'] = 'Chọn giới tính'
        if not ma_phong_an:   errors['ma_phong_an'] = 'Chọn phòng ăn'
        if not ma_phong_ngu:  errors['ma_phong_ngu'] = 'Chọn phòng ngủ'
        if errors:
            return JsonResponse({'ok': False, 'errors': errors}, status=400)

        try:
            phong_an  = Phong.objects.get(ma_phong=ma_phong_an)
        except Phong.DoesNotExist:
            return JsonResponse({'ok': False, 'errors': {'ma_phong_an': f'Phòng ăn "{ma_phong_an}" không tồn tại'}}, status=400)
        try:
            phong_ngu = Phong.objects.get(ma_phong=ma_phong_ngu)
        except Phong.DoesNotExist:
            return JsonResponse({'ok': False, 'errors': {'ma_phong_ngu': f'Phòng ngủ "{ma_phong_ngu}" không tồn tại'}}, status=400)

        if editing_id:
            hs = get_object_or_404(HocSinh, pk=editing_id)
        else:
            hs = HocSinh()

        hs.ho_ten      = ho_ten
        hs.lop         = lop
        hs.gioi_tinh   = int(gioi_tinh)
        hs.ma_phong_an = phong_an
        hs.ma_phong_ngu= phong_ngu
        hs.dang_hoc    = dang_hoc
        hs.ghi_chu     = ghi_chu or None

        hs.full_clean()
        hs.save()
        return JsonResponse({'ok': True, 'id': hs.pk, 'ho_ten': hs.ho_ten})

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

@require_POST
@role_required('admin')
def api_hocsinh_delete(request, pk):
    try:
        # Lấy tên trước khi update để đảm bảo ID tồn tại và có tên hiển thị Toast
        ten = HocSinh.objects.values_list('ho_ten', flat=True).get(pk=pk)
        
        # Chạy lệnh delete trực tiếp trên Database
        HocSinh.objects.filter(pk=pk).delete()
        return JsonResponse({'ok': True, 'ho_ten': ten})
    except HocSinh.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Không tìm thấy học sinh'}, status=404)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@role_required('admin')
def api_hocsinh_import_csv(request):
    """
    POST multipart/form-data với field 'file' là file CSV.
    Cấu trúc CSV (có header hoặc không):
      STT | Mã số BT | Họ và tên | GT | Lớp | Phòng ngủ | Phòng ăn | Ghi chú
    Cột GT chấp nhận: Nam/Nữ, 0/1, M/F (không phân biệt hoa thường)
    Trả về: {ok, total, success, errors: [{row, msg}]}
    """
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)

    uploaded = request.FILES.get('file')
    if not uploaded:
        return JsonResponse({'ok': False, 'error': 'Không tìm thấy file'}, status=400)

    # Đọc file với encoding UTF-8 (hoặc fallback latin-1)
    try:
        text = uploaded.read().decode('utf-8-sig')
    except UnicodeDecodeError:
        uploaded.seek(0)
        text = uploaded.read().decode('latin-1')

    reader = csv.reader(io.StringIO(text))
    results = {'ok': True, 'total': 0, 'success': 0, 'skipped': 0, 'errors': []}

    def parse_gt(val):
        """Chuyển GT sang 0/1. Raise ValueError nếu không nhận dạng được."""
        v = str(val).strip().lower()
        if v in ('0', 'nam', 'm', 'male'):
            return 0
        if v in ('1', 'nữ', 'nu', 'f', 'female', 'nư'):
            return 1
        raise ValueError(f'Giới tính không hợp lệ: "{val}"')

    for row_num, row in enumerate(reader, start=1):
        # Bỏ qua dòng rỗng
        if not any(cell.strip() for cell in row):
            continue

        # Bỏ qua dòng header (nếu có) – nhận dạng bằng cột đầu không phải số
        if row_num == 1:
            first = row[0].strip().lower()
            if not first.isdigit() and first in ('stt', '#', 'no', ''):
                results['skipped'] += 1
                continue

        results['total'] += 1

        try:
            # Cần ít nhất 7 cột (STT đến Phòng ăn). Cột Ghi chú tùy chọn.
            if len(row) < 7:
                raise ValueError(f'Dòng chỉ có {len(row)} cột, cần tối thiểu 7')

            # Cột 0: STT  (bỏ qua)
            # Cột 1: Mã số BT  (bỏ qua – id sẽ tự tăng)
            ho_ten       = row[2].strip()
            gioi_tinh    = parse_gt(row[3])
            lop          = row[4].strip().upper()
            ma_phong_ngu = row[5].strip().upper()
            ma_phong_an  = row[6].strip().upper()
            ghi_chu      = row[7].strip() if len(row) > 7 else ''

            if not ho_ten:
                raise ValueError('Họ tên không được để trống')
            if not lop:
                raise ValueError('Lớp không được để trống')
            if not ma_phong_ngu:
                raise ValueError('Phòng ngủ không được để trống')
            if not ma_phong_an:
                raise ValueError('Phòng ăn không được để trống')

            # Kiểm tra phòng tồn tại – báo lỗi rõ ràng nếu không có
            try:
                phong_an = Phong.objects.get(ma_phong=ma_phong_an)
            except Phong.DoesNotExist:
                raise ValueError(f'Phòng ăn "{ma_phong_an}" không tồn tại trong CSDL')

            try:
                phong_ngu = Phong.objects.get(ma_phong=ma_phong_ngu)
            except Phong.DoesNotExist:
                raise ValueError(f'Phòng ngủ "{ma_phong_ngu}" không tồn tại trong CSDL')

            ma_bt = row[1].strip()
            
            # Kiểm tra trùng theo Mã BT (ID) thay vì tên
            if ma_bt:
                if not ma_bt.isdigit():
                    raise ValueError(f'Mã BT "{ma_bt}" không hợp lệ (phải là số)')
                if HocSinh.objects.filter(pk=ma_bt).exists():
                    results['errors'].append({
                        'row': row_num,
                        'msg': f'Học sinh có Mã BT "{ma_bt}" đã tồn tại trong CSDL, bỏ qua.'
                    })
                    continue

            hs_kwargs = {
                'ho_ten': ho_ten,
                'gioi_tinh': gioi_tinh,
                'lop': lop,
                'ma_phong_an': phong_an,
                'ma_phong_ngu': phong_ngu,
                'ghi_chu': ghi_chu or None,
                'dang_hoc': True,
            }
            if ma_bt:
                hs_kwargs['id'] = int(ma_bt)

            hs = HocSinh(**hs_kwargs)
            hs.full_clean()
            hs.save()
            results['success'] += 1

        except Exception as e:
            results['errors'].append({'row': row_num, 'msg': str(e)})

    return JsonResponse(results)

@require_POST
@role_required('admin')
def api_phong_save(request):
    try:
        data = json.loads(request.body)
        ma_phong = data.get('ma_phong', '').strip().upper()
        loai_phong = data.get('loai_phong')
        suc_chua = data.get('suc_chua')
        gioi_tinh = data.get('gioi_tinh')  # có thể là None hoặc int
        sl_diem_danh = data.get('sl_diem_danh', 1)
        sl_ho_tro = data.get('sl_ho_tro', 1)
        ma_phong_old = data.get('ma_phong_old')  # khi sửa

        if not ma_phong or loai_phong is None or not suc_chua:
            return JsonResponse({'ok': False, 'error': 'Thiếu thông tin bắt buộc'}, status=400)

        if ma_phong_old:  # Sửa phòng
            ph = get_object_or_404(Phong, ma_phong=ma_phong_old)
            ph.loai_phong = int(loai_phong)
            ph.suc_chua = int(suc_chua)
            ph.gioi_tinh = int(gioi_tinh) if gioi_tinh is not None else None
            ph.sl_diem_danh = int(sl_diem_danh)
            ph.sl_ho_tro = int(sl_ho_tro)
            ph.full_clean()
            ph.save()
            return JsonResponse({'ok': True, 'ma_phong': ph.ma_phong})
        else:  # Thêm mới
            ph = Phong(
                ma_phong=ma_phong,
                loai_phong=int(loai_phong),
                suc_chua=int(suc_chua),
                gioi_tinh=int(gioi_tinh) if gioi_tinh is not None else None,
                sl_diem_danh=int(sl_diem_danh),
                sl_ho_tro=int(sl_ho_tro)
            )
            ph.full_clean()
            ph.save()
            return JsonResponse({'ok': True, 'ma_phong': ph.ma_phong})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

@require_POST
@role_required('admin')
def api_phong_delete(request):
    try:
        data = json.loads(request.body)
        ma = data.get('ma_phong', '').strip().upper()
        if not ma:
            return JsonResponse({'ok': False, 'error': 'Thiếu mã phòng'}, status=400)
        ph = get_object_or_404(Phong, ma_phong=ma)
        ph.delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)

@require_POST
@role_required('admin')
def api_giaovien_save(request):
    try:
        data = json.loads(request.body)
        if not data.get('so_dien_thoai'):
            data['so_dien_thoai'] = None

        editing_id = data.get('id')
        if editing_id:
            gv = get_object_or_404(GiaoVien, pk=editing_id)
            form = GiaoVienForm(data, instance=gv)
        else:
            form = GiaoVienForm(data)
        
        if form.is_valid():
            gv = form.save()
            return JsonResponse({'ok': True, 'id': gv.pk, 'ho_ten': gv.ho_ten})
        else:
            with open('error_log.txt', 'w', encoding='utf-8') as f: f.write(str(form.errors.get_json_data()))
            return JsonResponse({'ok': False, 'errors': form.errors.get_json_data()}, status=400)
    except Exception as e:
        with open('error_log.txt', 'w', encoding='utf-8') as f: f.write(str(e))
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

@require_POST
@role_required('admin')
def api_giaovien_delete(request, pk):
    gv = get_object_or_404(GiaoVien, pk=pk)
    # Hard delete (Xoá vĩnh viễn theo yêu cầu)
    gv.delete()
    return JsonResponse({'ok': True})


@require_POST
@role_required('admin')
def api_giaovien_ranh_save(request, pk):
    try:
        gv = get_object_or_404(GiaoVien, pk=pk)
        data = json.loads(request.body)
        lich_ranh = data.get('lich_ranh', [False]*5)
        gv.lich_ranh = lich_ranh
        gv.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

@require_POST
@role_required('admin', 'quan_ly')
def api_cauhinh_save(request):
    try:
        data = json.loads(request.body)
        an_val = data.get('an')
        ngu_val = data.get('ngu')
        today = date.today()
        user = request.user

        # Lưu vào CSDL - tạo bản ghi mới để giữ lịch sử + ghi người chỉnh sửa
        if an_val is not None:
            CauHinhGia.objects.update_or_create(
                loai_truc=LoaiTruc.AN, ngay_ap_dung=today,
                defaults={'don_gia': an_val, 'nguoi_cap_nhat': user}
            )
        if ngu_val is not None:
            CauHinhGia.objects.update_or_create(
                loai_truc=LoaiTruc.NGU, ngay_ap_dung=today,
                defaults={'don_gia': ngu_val, 'nguoi_cap_nhat': user}
            )

        ten_user = getattr(user, 'fullname', '') or user.username
        return JsonResponse({'ok': True, 'updated': today.strftime('%d/%m/%Y'), 'nguoi': ten_user})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

@require_POST
@role_required('admin', 'quan_ly')
def api_hethong_save(request):
    try:
        data = json.loads(request.body)
        ht = CauHinhHeThong.get()
        if 'nam_hoc' in data:
            ht.nam_hoc = data['nam_hoc'].strip()
        if 'nguoi_phu_trach' in data:
            ht.nguoi_phu_trach = data['nguoi_phu_trach'].strip()
        if 'ten_truong' in data:
            ht.ten_truong = data['ten_truong'].strip()
        ht.save()
        return JsonResponse({'ok': True, 'nam_hoc': ht.nam_hoc, 'nguoi_phu_trach': ht.nguoi_phu_trach})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)
@require_POST
@role_required('admin', 'quan_ly')
def api_vatdung_mua_save(request):
    try:
        data = json.loads(request.body)
        obj = MuaVatDung.objects.create(
            nam_hoc=data['nam_hoc'],
            lan_mua=data['lan_mua'],
            loai_vat_dung=data['loai'],
            so_luong=data['so_luong']
        )
        return JsonResponse({'ok': True, 'id': obj.pk, 'ngay_mua': obj.ngay_mua.isoformat()})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)

@require_POST
@role_required('admin', 'quan_ly')
def api_vatdung_mua_delete(request):
    try:
        data = json.loads(request.body)
        MuaVatDung.objects.filter(pk=data['id']).delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)

@require_POST
@role_required('admin', 'quan_ly')
def api_vatdung_phanbo_save(request):
    try:
        data = json.loads(request.body)
        mua = get_object_or_404(MuaVatDung, pk=data['mua_id'])
        phong = get_object_or_404(Phong, ma_phong=data['phong'])
        obj = PhanBoVatDung.objects.create(
            mua=mua,
            phong=phong,
            so_luong=data['so_luong']
        )
        return JsonResponse({'ok': True, 'id': obj.pk})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)

@require_POST
@role_required('admin', 'quan_ly')
def api_vatdung_phanbo_delete(request):
    try:
        data = json.loads(request.body)
        PhanBoVatDung.objects.filter(pk=data['id']).delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)
