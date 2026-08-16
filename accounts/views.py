from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.utils import timezone

from .forms import RegisterForm, LoginForm, ProfileUpdateForm, OTPVerifyForm
from .models import OTPCode
from .utils import generate_and_send_otp, send_login_otp, RESEND_COOLDOWN_SECONDS

LOGIN_ATTEMPT_LIMIT = 5
LOGIN_LOCKOUT_SECONDS = 300  # 5 minutes

OTP_ATTEMPT_LIMIT = 5
OTP_LOCKOUT_SECONDS = 300  # 5 minutes

PASSWORD_RESET_COOLDOWN_SECONDS = 60  # per submitted email, prevents inbox-flooding


def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def _throttle_key(request):
    return f'login_attempts:{_client_ip(request)}'


def _otp_attempt_key(user_id, purpose):
    return f'otp_attempts:{user_id}:{purpose}'


# ==========================================================
# Registration (creates the account, then requires an email OTP
# before the session is actually started)
# ==========================================================
def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_login_otp(user, purpose='register')
            request.session['otp_pending_user_id'] = user.pk
            request.session['otp_purpose'] = 'register'
            request.session['otp_next'] = ''
            messages.info(request, f'We sent a 6-digit verification code to {user.email}.')
            return redirect('accounts:verify_otp')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


# ==========================================================
# Login (step 1: verify credentials, then require an email OTP
# before actually starting the session — two-factor login)
# ==========================================================
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            key = _throttle_key(request)
            attempts = cache.get(key, 0)
            if attempts >= LOGIN_ATTEMPT_LIMIT:
                messages.error(request, 'Too many failed login attempts. Please try again in 5 minutes.')
                return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Credentials are correct, but do NOT start the session yet — send an OTP first.
        cache.delete(_throttle_key(self.request))
        user = form.get_user()
        send_login_otp(user, purpose='login')
        self.request.session['otp_pending_user_id'] = user.pk
        self.request.session['otp_purpose'] = 'login'
        self.request.session['otp_next'] = self.request.POST.get('next') or self.get_redirect_url() or ''
        messages.info(self.request, f'We sent a 6-digit verification code to {user.email}.')
        return redirect('accounts:verify_otp')

    def form_invalid(self, form):
        key = _throttle_key(self.request)
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, LOGIN_LOCKOUT_SECONDS)
        remaining = LOGIN_ATTEMPT_LIMIT - attempts
        if remaining <= 0:
            messages.error(self.request, 'Too many failed attempts. Login has been temporarily locked for 5 minutes.')
        elif remaining <= 2:
            messages.warning(self.request, f'Invalid username or password. {remaining} attempt(s) left before a temporary lock.')
        return super().form_invalid(form)


# ==========================================================
# OTP verification (shared by register + login flows)
# ==========================================================
def verify_otp(request):
    user_id = request.session.get('otp_pending_user_id')
    purpose = request.session.get('otp_purpose')

    if not user_id or purpose not in ('register', 'login'):
        messages.error(request, 'Your verification session has expired. Please log in or register again.')
        return redirect('accounts:login')

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        request.session.pop('otp_pending_user_id', None)
        return redirect('accounts:login')

    if request.method == 'POST':
        attempt_key = _otp_attempt_key(user.pk, purpose)
        attempts = cache.get(attempt_key, 0)

        if attempts >= OTP_ATTEMPT_LIMIT:
            messages.error(request, 'Too many incorrect attempts. Please request a new code and try again.')
            request.session.pop('otp_pending_user_id', None)
            request.session.pop('otp_purpose', None)
            request.session.pop('otp_next', None)
            return redirect('accounts:login')

        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            otp = OTPCode.objects.filter(user=user, purpose=purpose, code=code).order_by('-created_at').first()
            if otp and otp.is_valid():
                cache.delete(attempt_key)
                otp.is_used = True
                otp.save(update_fields=['is_used'])
                # Invalidate any other outstanding codes for this purpose.
                OTPCode.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)

                login(request, user)
                next_url = request.session.pop('otp_next', '') or 'core:home'
                request.session.pop('otp_pending_user_id', None)
                request.session.pop('otp_purpose', None)

                if purpose == 'register':
                    messages.success(request, f'Welcome to Furni, {user.first_name or user.username}! Your account is verified.')
                else:
                    messages.success(request, f'Welcome back, {user.first_name or user.username}!')

                return redirect(next_url if next_url.startswith('/') else 'core:home')
            elif otp and otp.is_expired():
                messages.error(request, 'This code has expired. Please request a new one.')
            else:
                attempts += 1
                cache.set(attempt_key, attempts, OTP_LOCKOUT_SECONDS)
                remaining = OTP_ATTEMPT_LIMIT - attempts
                if remaining <= 0:
                    messages.error(request, 'Too many incorrect attempts. Please request a new code and try again.')
                    request.session.pop('otp_pending_user_id', None)
                    request.session.pop('otp_purpose', None)
                    request.session.pop('otp_next', None)
                    return redirect('accounts:login')
                elif remaining <= 2:
                    messages.warning(request, f'Invalid verification code. {remaining} attempt(s) left before you must request a new one.')
                else:
                    messages.error(request, 'Invalid verification code. Please try again.')
    else:
        form = OTPVerifyForm()

    can_resend = True
    last_otp = OTPCode.objects.filter(user=user, purpose=purpose).order_by('-created_at').first()
    seconds_left = 0
    if last_otp:
        elapsed = (timezone.now() - last_otp.created_at).total_seconds()
        if elapsed < RESEND_COOLDOWN_SECONDS:
            can_resend = False
            seconds_left = int(RESEND_COOLDOWN_SECONDS - elapsed)

    context = {
        'form': form,
        'email': user.email,
        'purpose': purpose,
        'can_resend': can_resend,
        'seconds_left': seconds_left,
    }
    return render(request, 'accounts/verify_otp.html', context)


def resend_otp(request):
    user_id = request.session.get('otp_pending_user_id')
    purpose = request.session.get('otp_purpose')
    if not user_id or purpose not in ('register', 'login'):
        return redirect('accounts:login')

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return redirect('accounts:login')

    last_otp = OTPCode.objects.filter(user=user, purpose=purpose).order_by('-created_at').first()
    if last_otp:
        elapsed = (timezone.now() - last_otp.created_at).total_seconds()
        if elapsed < RESEND_COOLDOWN_SECONDS:
            messages.warning(request, 'Please wait a moment before requesting another code.')
            return redirect('accounts:verify_otp')

    generate_and_send_otp(user, purpose=purpose)
    cache.delete(_otp_attempt_key(user.pk, purpose))
    messages.success(request, f'A new verification code was sent to {user.email}.')
    return redirect('accounts:verify_otp')


def cancel_otp(request):
    request.session.pop('otp_pending_user_id', None)
    request.session.pop('otp_purpose', None)
    request.session.pop('otp_next', None)
    return redirect('accounts:login')


class ThrottledPasswordResetView(PasswordResetView):
    """Same behavior as Django's PasswordResetView, but protects against
    someone repeatedly submitting a victim's email to flood their inbox
    with password-reset links.

    The cooldown is keyed by the submitted email address (not the caller's
    IP), because the goal is to protect the *target* inbox regardless of
    who is sending the requests. To avoid leaking whether an email exists
    in the system, throttled requests still redirect to the same generic
    success page — they just silently skip actually sending another email.
    """

    def form_valid(self, form):
        email = (form.cleaned_data.get('email') or '').strip().lower()
        key = f'password_reset_cooldown:{email}'
        if email and cache.get(key):
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
        if email:
            cache.set(key, True, PASSWORD_RESET_COOLDOWN_SECONDS)
        return super().form_valid(form)


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out successfully. See you soon!")
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
            messages.success(request, 'Your profile has been updated successfully.')
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
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    for field in form.fields.values():
        field.widget.attrs.update({'class': 'form-control'})
    return render(request, 'accounts/change_password.html', {'form': form})
