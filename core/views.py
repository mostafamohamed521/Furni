from django.shortcuts import render, redirect
from django.contrib import messages
from shop.models import Product, Category
from blog.models import Post
from .models import Testimonial, TeamMember, Service, SiteSetting, FAQ, LegalPage
from .forms import ContactForm


def home(request):
    context = {
        'featured_products': Product.objects.filter(is_active=True, is_featured=True)[:4],
        'popular_products': Product.objects.filter(is_active=True, is_popular=True)[:3] or Product.objects.filter(is_active=True)[:3],
        'testimonials': Testimonial.objects.filter(is_active=True),
        'recent_posts': Post.objects.filter(is_published=True)[:3],
        'categories': Category.objects.filter(is_active=True)[:6],
    }
    return render(request, 'core/index.html', context)


def about(request):
    context = {
        'team_members': TeamMember.objects.all(),
        'testimonials': Testimonial.objects.filter(is_active=True),
    }
    return render(request, 'core/about.html', context)


def services(request):
    context = {
        'services': Service.objects.all(),
    }
    return render(request, 'core/services.html', context)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for reaching out! We'll get back to you as soon as possible.")
            return redirect('core:contact')
    else:
        form = ContactForm()
    context = {
        'form': form,
        'site_settings': SiteSetting.load(),
    }
    return render(request, 'core/contact.html', context)


def faq(request):
    context = {'faqs': FAQ.objects.filter(is_active=True)}
    return render(request, 'core/faq.html', context)


def terms(request):
    page, _ = LegalPage.objects.get_or_create(page_type='terms', defaults={
        'title': 'Terms & Conditions',
        'content': '<p>Terms & conditions content will be updated soon.</p>',
    })
    return render(request, 'core/legal_page.html', {'page': page})


def privacy(request):
    page, _ = LegalPage.objects.get_or_create(page_type='privacy', defaults={
        'title': 'Privacy Policy',
        'content': '<p>Privacy policy content will be updated soon.</p>',
    })
    return render(request, 'core/legal_page.html', {'page': page})


def custom_404(request, exception):
    return render(request, 'core/404.html', status=404)


def custom_500(request):
    return render(request, 'core/500.html', status=500)
