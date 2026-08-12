from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import SubscriberForm


@require_POST
def subscribe(request):
    form = SubscriberForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Thanks for subscribing to our newsletter!')
    else:
        if 'email' in form.errors:
            messages.error(request, 'This email is already subscribed or invalid.')
        else:
            messages.error(request, 'Something went wrong. Please try again.')
    return redirect(request.META.get('HTTP_REFERER', '/'))
