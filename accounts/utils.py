import random
from django.core.mail import send_mail
from django.conf import settings

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
