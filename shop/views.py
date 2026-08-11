from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from .models import Category, Product, Wishlist
from .forms import ReviewForm


PRODUCTS_PER_PAGE = 9


def shop_list(request):
    products = Product.objects.filter(is_active=True).select_related('category')

    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=selected_category)

    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(short_description__icontains=query)
        )

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort = request.GET.get('sort', 'newest')
    sort_map = {
        'newest': '-created_at',
        'price_low': 'price',
        'price_high': '-price',
        'name': 'name',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': Category.objects.filter(is_active=True),
        'selected_category': selected_category,
        'query': query,
        'sort': sort,
        'total_results': paginator.count,
    }
    return render(request, 'shop/shop.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    return redirect(f"/shop/?category={category.slug}")


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug, is_active=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    reviews = product.reviews.filter(is_approved=True).select_related('user')

    user_has_reviewed = False
    review_form = ReviewForm()
    if request.user.is_authenticated:
        user_has_reviewed = reviews.filter(user=request.user).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        if user_has_reviewed:
            messages.warning(request, 'لقد قمت بتقييم هذا المنتج من قبل.')
            return redirect(product.get_absolute_url())
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'شكراً لك! تم إضافة تقييمك بنجاح.')
            return redirect(product.get_absolute_url())
    elif request.method == 'POST':
        messages.info(request, 'الرجاء تسجيل الدخول لإضافة تقييم.')
        return redirect('accounts:login')

    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'review_form': review_form,
        'user_has_reviewed': user_has_reviewed,
        'is_wishlisted': is_wishlisted,
    }
    return render(request, 'shop/product_detail.html', context)


@login_required
def toggle_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        wishlist_item.delete()
        added = False
        messages.info(request, f'تمت إزالة "{product.name}" من قائمة الرغبات.')
    else:
        added = True
        messages.success(request, f'تمت إضافة "{product.name}" إلى قائمة الرغبات.')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'added': added})
    return redirect(request.META.get('HTTP_REFERER', product.get_absolute_url()))


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'shop/wishlist.html', {'items': items})


def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    results = []
    if len(query) >= 2:
        products = Product.objects.filter(is_active=True, name__icontains=query)[:6]
        results = [{'name': p.name, 'url': p.get_absolute_url(), 'price': str(p.price),
                    'image': p.image.url if p.image else ''} for p in products]
    return JsonResponse({'results': results})
