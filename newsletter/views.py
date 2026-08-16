from django.shortcuts import redirect, render
from django.contrib import messages
from django.views.decorators.http import require_POST

from .forms import SubscriberForm
from .models import Subscriber
from .utils import verify_unsubscribe_token


@require_POST
def subscribe(request):
    form = SubscriberForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Thanks for subscribing to our newsletter! You can unsubscribe at any time using the link in any email we send you.')
    else:
        if 'email' in form.errors:
            messages.error(request, 'This email is already subscribed or invalid.')
        else:
            messages.error(request, 'Something went wrong. Please try again.')
    return redirect(request.META.get('HTTP_REFERER', '/'))


def unsubscribe(request, token):
    email = verify_unsubscribe_token(token)
    if not email:
        return render(request, 'newsletter/unsubscribe.html', {'success': False})

    updated = Subscriber.objects.filter(email__iexact=email).update(is_active=False)
    return render(request, 'newsletter/unsubscribe.html', {'success': bool(updated), 'email': email})
