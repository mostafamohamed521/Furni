from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse


def send_order_confirmation_email(order, request=None):
    """Email the customer a plain-text summary of their order right after
    checkout. Uses the same EMAIL_BACKEND as everything else (console in
    development, real SMTP once configured in .env for production) — see
    accounts/utils.py for the equivalent OTP-sending helper.
    """
    track_path = reverse('orders:track_order')
    site_url = request.build_absolute_uri('/').rstrip('/') if request else ''

    subject = f'Your Furni order {order.order_number} is confirmed'
    message = render_to_string('orders/emails/order_confirmation.txt', {
        'order': order,
        'items': order.items.all(),
        'site_name': getattr(settings, 'SITE_NAME', 'Furni'),
        'site_url': site_url,
        'track_path': track_path,
    })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.email], fail_silently=True)
