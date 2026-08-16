from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override'])
        messages.success(request, f'"{product.name}" was added to your cart.')
    else:
        messages.error(request, 'Please enter a valid quantity.')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'total_items': len(cart), 'total_price': str(cart.get_total_price())})

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'cart:cart_detail'
    return redirect(next_url)


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f'"{product.name}" was removed from your cart.')
    return redirect('cart:cart_detail')


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    if quantity < 1:
        cart.remove(product)
    else:
        cart.add(product=product, quantity=quantity, override_quantity=True)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        item_total = None
        for item in cart:
            if item['product'].id == product.id:
                item_total = str(item['total_price'])
        return JsonResponse({
            'total_items': len(cart),
            'total_price': str(cart.get_total_price()),
            'item_total': item_total,
        })
    return redirect('cart:cart_detail')


@require_POST
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    messages.info(request, 'Your cart has been cleared.')
    return redirect('cart:cart_detail')
