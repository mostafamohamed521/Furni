from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from cart.cart import Cart
from .forms import OrderCreateForm, CouponApplyForm, TrackOrderForm
from .models import Order, OrderItem, Coupon
from .utils import send_order_confirmation_email
from shop.models import Product


class _StockUnavailable(Exception):
    """Internal control-flow signal: raised inside the atomic block to force
    a rollback when stock isn't sufficient, then caught right outside it."""
    pass


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty. Please add some products first.')
        return redirect('shop:shop_list')

    coupon_code = request.session.get('coupon_code')
    discount_amount = Decimal('0')
    coupon = None
    if coupon_code:
        coupon = Coupon.objects.filter(code__iexact=coupon_code, active=True).first()
        if coupon:
            discount_amount = (cart.get_total_price() * coupon.discount_percent) / 100

    subtotal = cart.get_total_price()
    shipping_cost = Decimal('0') if subtotal >= settings.FREE_SHIPPING_THRESHOLD else Decimal(settings.SHIPPING_COST)
    grand_total = subtotal + shipping_cost - discount_amount

    initial = {}
    if request.user.is_authenticated:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        profile = getattr(request.user, 'profile', None)
        if profile:
            initial.update({
                'phone': profile.phone,
                'address': profile.address,
                'state': profile.city,
                'postal_code': profile.postal_code,
                'country': profile.country,
            })

    if request.method == 'POST':
        form = OrderCreateForm(request.POST, initial=initial)
        if form.is_valid():
            # Lock each product row for the duration of the transaction so two
            # concurrent checkouts for the same last-in-stock item can't both
            # succeed (a classic race condition that would oversell stock).
            # We validate availability BEFORE creating the order, so a
            # customer is never charged for an item that turns out to be
            # unavailable at the exact moment of checkout.
            product_ids = [item['product'].id for item in cart]
            try:
                with transaction.atomic():
                    locked_products = {
                        p.id: p for p in Product.objects.select_for_update().filter(id__in=product_ids)
                    }

                    insufficient = []
                    for item in cart:
                        locked_product = locked_products.get(item['product'].id)
                        if not locked_product or locked_product.stock < item['quantity']:
                            insufficient.append((locked_product, item['quantity']))

                    if insufficient:
                        for locked_product, requested_qty in insufficient:
                            if locked_product:
                                messages.error(
                                    request,
                                    f'Sorry, only {locked_product.stock} unit(s) of "{locked_product.name}" '
                                    f'are left in stock (you requested {requested_qty}). Please update your cart.'
                                )
                        raise _StockUnavailable()

                    order = form.save(commit=False)
                    if request.user.is_authenticated:
                        order.user = request.user
                    order.coupon = coupon
                    order.discount_amount = discount_amount
                    order.shipping_cost = shipping_cost
                    order.save()

                    for item in cart:
                        locked_product = locked_products[item['product'].id]
                        OrderItem.objects.create(
                            order=order,
                            product=locked_product,
                            product_name=locked_product.name,
                            price=item['price'],
                            quantity=item['quantity'],
                        )
                        locked_product.stock -= item['quantity']
                        locked_product.save(update_fields=['stock'])
            except _StockUnavailable:
                return redirect('cart:cart_detail')

            cart.clear()
            request.session.pop('coupon_code', None)
            # Remember this order in the session so only the person who just
            # placed it (or a logged-in owner) can view its full details.
            recent_orders = request.session.get('recent_guest_orders', [])
            recent_orders.append(order.order_number)
            request.session['recent_guest_orders'] = recent_orders[-10:]
            send_order_confirmation_email(order, request=request)
            return redirect('orders:thank_you', order_number=order.order_number)
    else:
        form = OrderCreateForm(initial=initial)

    coupon_form = CouponApplyForm()

    context = {
        'form': form,
        'coupon_form': coupon_form,
        'cart': cart,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'discount_amount': discount_amount,
        'grand_total': grand_total,
        'coupon': coupon,
    }
    return render(request, 'orders/checkout.html', context)


def apply_coupon(request):
    if request.method == 'POST':
        form = CouponApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            coupon = Coupon.objects.filter(code__iexact=code, active=True).first()
            if coupon:
                request.session['coupon_code'] = coupon.code
                messages.success(request, f'Coupon "{coupon.code}" applied successfully ({coupon.discount_percent}% off).')
            else:
                messages.error(request, 'This coupon code is invalid or no longer active.')
    return redirect('orders:checkout')


def thank_you(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    is_owner = (
        (request.user.is_authenticated and order.user_id == request.user.id)
        or order.order_number in request.session.get('recent_guest_orders', [])
    )
    if not is_owner:
        messages.info(request, 'To view this order, please use the Track Order page with the email used at checkout.')
        return redirect('orders:track_order')

    return render(request, 'orders/thankyou.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


def track_order(request):
    order = None
    searched = False
    if request.method == 'POST':
        form = TrackOrderForm(request.POST)
        searched = True
        if form.is_valid():
            order = Order.objects.filter(
                order_number__iexact=form.cleaned_data['order_number'],
                email__iexact=form.cleaned_data['email'],
            ).first()
            if not order:
                messages.error(request, 'No matching order was found. Please check the order number and email.')
    else:
        form = TrackOrderForm()

    context = {'form': form, 'order': order, 'searched': searched}
    return render(request, 'orders/track_order.html', context)
