import random
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import OTPCode

RESEND_COOLDOWN_SECONDS = 30


def generate_and_send_otp(user, purpose):
    """Create a fresh 6-digit OTP for the user and email it.

    In development (console email backend) the code is printed to the
    server console/terminal instead of actually being emailed.
    """
    code = f'{random.randint(0, 999999):06d}'
    OTPCode.objects.create(user=user, code=code, purpose=purpose)

    subject = 'Your Furni verification code'
    message = (
        f'Hi {user.first_name or user.username},\n\n'
        f'Your Furni verification code is: {code}\n'
        f'This code expires in {OTPCode.VALIDITY_MINUTES} minutes.\n\n'
        f"If you didn't request this, you can safely ignore this email.\n\n"
        f'— The Furni Team'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
    return code


def send_login_otp(user, purpose):
    """Send an OTP for a fresh login/register attempt, but respect the same
    cooldown window as the "resend" button.

    Without this, someone who already knows a valid password could spam the
    login form repeatedly to flood the account owner's inbox with codes
    (email bombing) — every successful password check would otherwise
    trigger a brand new email. If a still-valid code was already sent very
    recently, we simply reuse it instead of generating/emailing a new one.
    """
    last_otp = OTPCode.objects.filter(user=user, purpose=purpose, is_used=False).order_by('-created_at').first()
    if last_otp and not last_otp.is_expired():
        elapsed = (timezone.now() - last_otp.created_at).total_seconds()
        if elapsed < RESEND_COOLDOWN_SECONDS:
            return last_otp.code
    return generate_and_send_otp(user, purpose)
