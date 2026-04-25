"""
accounts/views.py
Quản lý tài khoản nội bộ – chỉ Admin mới truy cập được.
+ Trang cá nhân (profile) – mọi user đã đăng nhập.
"""
import json
import random
import time
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_http_methods

from accounts.decorators import role_required
from .models import StaffUser


@login_required(login_url='/login/')
@role_required('admin')
def quan_ly_taikhoan(request):
    """Trang quản lý tài khoản người dùng."""
    users = StaffUser.objects.all().order_by('fullname')
    return render(request, 'accounts/taikhoan.html', {
        'users': users,
        'role_choices': StaffUser.ROLE_CHOICES,
    })


@login_required(login_url='/login/')
@role_required('admin')
def api_taikhoan_list(request):
    """GET /api/taikhoan/ – danh sách tài khoản dạng JSON."""
    users = StaffUser.objects.all().order_by('fullname').values(
        'id', 'username', 'fullname', 'position', 'role', 'is_active', 'date_joined'
    )
    data = []
    for u in users:
        u['date_joined'] = u['date_joined'].strftime('%d/%m/%Y') if u['date_joined'] else ''
        data.append(u)
    return JsonResponse({'users': data})


@login_required(login_url='/login/')
@role_required('admin')
@require_POST
def api_taikhoan_save(request):
    """POST /api/taikhoan/save/ – tạo mới hoặc cập nhật tài khoản."""
    try:
        body = json.loads(request.body)
        uid  = body.get('id')

        if uid:
            # ── CẬP NHẬT ──
            user = StaffUser.objects.get(pk=uid)
            # Kiểm tra username trùng (trừ chính user này)
            uname = body.get('username', '').strip()
            if uname and uname != user.username:
                if StaffUser.objects.filter(username=uname).exists():
                    return JsonResponse({'ok': False, 'error': 'Tên đăng nhập đã tồn tại!'}, status=400)
                user.username = uname
        else:
            # ── TẠO MỚI ──
            uname = body.get('username', '').strip()
            if not uname:
                return JsonResponse({'ok': False, 'error': 'Vui lòng nhập tên đăng nhập!'}, status=400)
            if StaffUser.objects.filter(username=uname).exists():
                return JsonResponse({'ok': False, 'error': 'Tên đăng nhập đã tồn tại!'}, status=400)
            user = StaffUser(username=uname)

        user.fullname  = body.get('fullname', '').strip()
        user.position  = body.get('position', '').strip()
        user.role      = body.get('role', StaffUser.ROLE_KE_TOAN)
        user.is_active = body.get('is_active', True)

        # Nếu có mật khẩu mới thì cập nhật
        pw = body.get('password', '').strip()
        if pw:
            user.set_password(pw)
        elif not uid:
            return JsonResponse({'ok': False, 'error': 'Vui lòng nhập mật khẩu!'}, status=400)

        user.save()
        return JsonResponse({'ok': True, 'id': user.pk, 'msg': 'Đã lưu tài khoản!'})
    except StaffUser.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Không tìm thấy tài khoản!'}, status=404)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required(login_url='/login/')
@role_required('admin')
@require_POST
def api_taikhoan_delete(request):
    """POST /api/taikhoan/delete/ – xóa tài khoản."""
    try:
        body = json.loads(request.body)
        uid  = body.get('id')
        user = StaffUser.objects.get(pk=uid)
        # Không cho xóa chính mình
        if user.pk == request.user.pk:
            return JsonResponse({'ok': False, 'error': 'Không thể xóa tài khoản đang đăng nhập!'}, status=400)
        # Không cho xóa tài khoản gốc 'admin'
        if user.username == 'admin':
            return JsonResponse({'ok': False, 'error': 'Không thể xóa tài khoản admin gốc của hệ thống!'}, status=400)
        username = user.username
        user.delete()
        return JsonResponse({'ok': True, 'msg': f'Đã xóa tài khoản "{username}"!'})
    except StaffUser.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Không tìm thấy tài khoản!'}, status=404)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required(login_url='/login/')
@role_required('admin')
@require_POST
def api_taikhoan_reset_password(request):
    """POST /api/taikhoan/reset-pw/ – đặt lại mật khẩu."""
    try:
        body = json.loads(request.body)
        uid  = body.get('id')
        pw   = body.get('password', '').strip()
        if not pw:
            return JsonResponse({'ok': False, 'error': 'Vui lòng nhập mật khẩu mới!'}, status=400)
        if len(pw) < 6:
            return JsonResponse({'ok': False, 'error': 'Mật khẩu phải có ít nhất 6 ký tự!'}, status=400)
        user = StaffUser.objects.get(pk=uid)
        user.set_password(pw)
        user.save()
        return JsonResponse({'ok': True, 'msg': f'Đã đặt lại mật khẩu cho "{user.username}"!'})
    except StaffUser.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Không tìm thấy tài khoản!'}, status=404)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


# =====================================================================
#  PROFILE – CÁ NHÂN (Mọi user đã đăng nhập)
# =====================================================================

@login_required(login_url='/login/')
def profile_page(request):
    """Trang hồ sơ cá nhân."""
    return render(request, 'accounts/profile.html')


@login_required(login_url='/login/')
@require_POST
def api_profile_save(request):
    """POST /api/profile/save/ – Cập nhật thông tin cá nhân."""
    try:
        body = json.loads(request.body)
        user = request.user

        user.fullname = body.get('fullname', '').strip()
        user.position = body.get('position', '').strip()
        user.email    = body.get('email', '').strip()
        user.save()

        return JsonResponse({
            'ok': True,
            'msg': 'Đã cập nhật thông tin cá nhân!',
            'fullname': user.fullname,
            'username': user.username,
        })
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


def _mask_email(email):
    """Che bớt email: abc@gmail.com → a***c@gmail.com"""
    if not email or '@' not in email:
        return email
    local, domain = email.rsplit('@', 1)
    if len(local) <= 2:
        masked = local[0] + '***'
    else:
        masked = local[0] + '***' + local[-1]
    return f"{masked}@{domain}"


@login_required(login_url='/login/')
@require_POST
def api_profile_send_otp(request):
    """
    POST /api/profile/send-otp/
    Bước 1: Kiểm tra mật khẩu cũ → gửi OTP qua email.
    Lưu OTP + new_password hash vào session.
    """
    try:
        body = json.loads(request.body)
        current_pw = body.get('current_password', '')
        new_pw     = body.get('new_password', '')
        user = request.user

        # 1) Validate current password
        if not user.check_password(current_pw):
            return JsonResponse({'ok': False, 'error': 'Mật khẩu hiện tại không đúng!'}, status=400)

        # 2) Validate new password
        if not new_pw or len(new_pw) < 6:
            return JsonResponse({'ok': False, 'error': 'Mật khẩu mới phải có ít nhất 6 ký tự!'}, status=400)

        # 3) Check email
        if not user.email:
            return JsonResponse({'ok': False, 'error': 'Vui lòng cập nhật email trước khi đổi mật khẩu!'}, status=400)

        # 4) Generate OTP (6 digits)
        otp_code = f"{random.randint(0, 999999):06d}"

        # 5) Store in session
        request.session['pw_otp_code']   = otp_code
        request.session['pw_otp_time']   = time.time()
        request.session['pw_new_password'] = new_pw  # plain text, will be hashed on verify

        # 6) Send email
        try:
            send_mail(
                subject='[QL Bán trú] Mã xác thực đổi mật khẩu',
                message=f'Xin chào {user.fullname or user.username},\n\n'
                        f'Mã xác thực (OTP) của bạn là: {otp_code}\n\n'
                        f'Mã có hiệu lực trong 5 phút. Vui lòng không chia sẻ mã này với bất kỳ ai.\n\n'
                        f'Trân trọng,\n'
                        f'Hệ thống Quản lý Bán trú – THPT Lê Thị Hồng Gấm',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as mail_err:
            return JsonResponse({
                'ok': False,
                'error': f'Không thể gửi email. Vui lòng kiểm tra cấu hình email hệ thống. ({mail_err})'
            }, status=500)

        return JsonResponse({
            'ok': True,
            'msg': 'Mã OTP đã được gửi đến email của bạn!',
            'email_masked': _mask_email(user.email),
        })

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required(login_url='/login/')
@require_POST
def api_profile_verify_otp(request):
    """
    POST /api/profile/verify-otp/
    Bước 2: Xác thực OTP → đổi mật khẩu.
    """
    try:
        body = json.loads(request.body)
        otp_input = body.get('otp_code', '').strip()

        stored_otp  = request.session.get('pw_otp_code')
        stored_time = request.session.get('pw_otp_time')
        new_pw      = request.session.get('pw_new_password')

        if not stored_otp or not stored_time or not new_pw:
            return JsonResponse({'ok': False, 'error': 'Phiên xác thực đã hết hạn. Vui lòng gửi lại mã OTP!'}, status=400)

        # Check expiry (5 minutes)
        if time.time() - stored_time > 300:
            # Clear session data
            for k in ('pw_otp_code', 'pw_otp_time', 'pw_new_password'):
                request.session.pop(k, None)
            return JsonResponse({'ok': False, 'error': 'Mã OTP đã hết hạn! Vui lòng gửi lại mã mới.'}, status=400)

        # Verify OTP
        if otp_input != stored_otp:
            return JsonResponse({'ok': False, 'error': 'Mã OTP không đúng!'}, status=400)

        # Change password
        user = request.user
        user.set_password(new_pw)
        user.save()

        # Keep session alive after password change
        update_session_auth_hash(request, user)

        # Clear session data
        for k in ('pw_otp_code', 'pw_otp_time', 'pw_new_password'):
            request.session.pop(k, None)

        return JsonResponse({'ok': True, 'msg': 'Đổi mật khẩu thành công!'})

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)
