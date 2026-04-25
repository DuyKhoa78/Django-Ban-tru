"""
accounts/decorators.py
Decorator kiểm tra vai trò (role) của người dùng.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse


def role_required(*roles):
    """
    Bảo vệ view: chỉ cho phép user có role nằm trong `roles`.

    Ví dụ:
        @role_required('admin', 'hoc_vu')
        def my_view(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # AJAX request → trả JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' \
                        or request.content_type == 'application/json' \
                        or request.path.startswith('/api/'):
                    return JsonResponse({'ok': False, 'error': 'Chưa đăng nhập'}, status=401)
                return redirect('login')

            user = request.user
            # superuser luôn pass
            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            if hasattr(user, 'role') and user.role in roles:
                return view_func(request, *args, **kwargs)

            # AJAX/API request → trả JSON 403
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' \
                    or request.content_type == 'application/json' \
                    or request.path.startswith('/api/'):
                return JsonResponse({'ok': False, 'error': 'Không có quyền thực hiện thao tác này'}, status=403)

            messages.error(request, 'Bạn không có quyền truy cập trang này.')
            return redirect('index')
        return wrapper
    return decorator
