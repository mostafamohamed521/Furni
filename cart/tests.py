from django.test import TestCase
from django.urls import reverse

from shop.models import Product
from .cart import Cart


class CartTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Cart Item', price=30, stock=10)

    def test_add_to_cart(self):
        self.client.post(reverse('cart:cart_add', args=[self.product.id]), {'quantity': 2, 'override': 'False'})
        resp = self.client.get(reverse('cart:cart_detail'))
        self.assertContains(resp, 'Cart Item')

    def test_garbage_quantity_on_update_does_not_crash(self):
        self.client.post(reverse('cart:cart_add', args=[self.product.id]), {'quantity': 1, 'override': 'False'})
        resp = self.client.post(reverse('cart:cart_update', args=[self.product.id]), {'quantity': 'garbage'})
        self.assertIn(resp.status_code, (200, 302))

    def test_cart_cannot_exceed_available_stock(self):
        self.client.post(reverse('cart:cart_add', args=[self.product.id]), {'quantity': 999, 'override': 'True'})
        session = self.client.session
        cart_data = session.get('cart', {})
        self.assertLessEqual(cart_data[str(self.product.id)]['quantity'], self.product.stock)

    def test_clear_cart(self):
        self.client.post(reverse('cart:cart_add', args=[self.product.id]), {'quantity': 1, 'override': 'False'})
        self.client.post(reverse('cart:cart_clear'))
        # Check the actual cart contents (session state + empty-state markup),
        # not the page text in general — an earlier "added to cart" toast
        # message can still be queued for display and would give a false
        # positive if we just searched the whole page for the product name.
        self.assertEqual(self.client.session.get('cart'), {})
        resp = self.client.get(reverse('cart:cart_detail'))
        self.assertContains(resp, 'empty-state')
