from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.core.exceptions import ValidationError

from .forms import RegisterForm, LoginForm, ProfileUpdateForm

LOGIN_ATTEMPT_LIMIT = 5
LOGIN_LOCKOUT_SECONDS = 300  # 5 minutes


def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def _throttle_key(request):
    return f'login_attempts:{_client_ip(request)}'


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'مرحباً بك {user.first_name}! تم إنشاء حسابك بنجاح.')
            return redirect('core:home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            key = _throttle_key(request)
            attempts = cache.get(key, 0)
            if attempts >= LOGIN_ATTEMPT_LIMIT:
                messages.error(request, 'تم إيقاف محاولات الدخول مؤقتاً بسبب محاولات فاشلة متكررة. الرجاء المحاولة بعد 5 دقائق.')
                return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        cache.delete(_throttle_key(self.request))
        messages.success(self.request, f'مرحباً بعودتك، {form.get_user().first_name or form.get_user().username}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        key = _throttle_key(self.request)
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, LOGIN_LOCKOUT_SECONDS)
        remaining = LOGIN_ATTEMPT_LIMIT - attempts
        if remaining <= 0:
            messages.error(self.request, 'تم تجاوز عدد المحاولات المسموح بها. تم إيقاف الدخول مؤقتاً لمدة 5 دقائق.')
        elif remaining <= 2:
            messages.warning(self.request, f'بيانات الدخول غير صحيحة. لديك {remaining} محاولة/محاولات متبقية قبل الإيقاف المؤقت.')
        return super().form_invalid(form)


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح. نراك قريباً!')
    return redirect('core:home')


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, 'تم تحديث بياناتك بنجاح.')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'تم تغيير كلمة المرور بنجاح.')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    for field in form.fields.values():
        field.widget.attrs.update({'class': 'form-control'})
    return render(request, 'accounts/change_password.html', {'form': form})
