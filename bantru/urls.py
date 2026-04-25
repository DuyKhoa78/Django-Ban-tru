from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


class RememberMeLoginView(auth_views.LoginView):
    """LoginView có hỗ trợ 'Ghi nhớ đăng nhập'."""
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        remember = self.request.POST.get('remember')
        if not remember:
            # Không ghi nhớ → session hết hạn khi đóng trình duyệt
            self.request.session.set_expiry(0)
        else:
            # Ghi nhớ → session tồn tại 30 ngày
            self.request.session.set_expiry(60 * 60 * 24 * 30)
        return super().form_valid(form)


urlpatterns = [
    path('sys-admin/', admin.site.urls),

    # ── Auth ──
    path('login/',  RememberMeLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),

    # ── Apps ──
    path('', include('core.urls')),
    path('', include('quanli.urls')),
    path('', include('nghiepvu.urls')),
    path('', include('accounts.urls')),
]
