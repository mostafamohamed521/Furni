from .cart import Cart


def cart_processor(request):
    cart = Cart(request)
    return {
        'cart_total_items': len(cart),
        'cart_total_price': cart.get_total_price(),
    }
