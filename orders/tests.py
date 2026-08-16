from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from shop.models import Product
from .models import Order


CHECKOUT_DATA = {
    'country': 'EG', 'first_name': 'Test', 'last_name': 'Buyer',
    'address': '1 Test St', 'state': 'Cairo', 'postal_code': '11111',
    'email': 'buyer@example.com', 'phone': '+201234567890',
    'payment_method': 'cod',
}


class StockRaceConditionTests(TestCase):
    """Covers: checkout locks stock atomically so a customer is never
    charged for more than what's actually available, and stock never
    goes negative."""

    def setUp(self):
        self.product = Product.objects.create(name='Limited Item', price=50, stock=1)

    def _add_to_cart(self, quantity):
        return self.client.post(reverse('cart:cart_add', args=[self.product.id]), {
            'quantity': quantity, 'override': 'True',
        })

    def test_checkout_rejected_when_stock_drops_after_add_to_cart(self):
        self._add_to_cart(1)
        # Simulate stock disappearing after the item was already in the cart
        self.product.stock = 0
        self.product.save(update_fields=['stock'])

        orders_before = Order.objects.count()
        self.client.post(reverse('orders:checkout'), CHECKOUT_DATA)

        self.assertEqual(Order.objects.count(), orders_before)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 0)

    def test_successful_checkout_decrements_stock(self):
        self.product.stock = 5
        self.product.save(update_fields=['stock'])
        self._add_to_cart(2)
        resp = self.client.post(reverse('orders:checkout'), CHECKOUT_DATA, follow=True)
        self.assertTrue(any('thank-you' in url for url, code in resp.redirect_chain))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)


class OrderConfirmationEmailTests(TestCase):
    """Covers: a confirmation email is sent after checkout, and special
    characters in the customer's name/address are not HTML-escaped into
    garbled entities in the plain-text email."""

    def setUp(self):
        self.product = Product.objects.create(name='Emailed Item', price=20, stock=10)
        self.client.post(reverse('cart:cart_add', args=[self.product.id]), {'quantity': 1, 'override': 'True'})

    def test_confirmation_email_sent_on_success(self):
        from django.core import mail
        self.client.post(reverse('orders:checkout'), CHECKOUT_DATA)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('order', mail.outbox[0].subject.lower())

    def test_special_characters_not_escaped_in_email(self):
        from django.core import mail
        data = dict(CHECKOUT_DATA, first_name="O'Brien & Sons")
        self.client.post(reverse('orders:checkout'), data)
        body = mail.outbox[0].body
        self.assertIn("O'Brien & Sons", body)
        self.assertNotIn('&amp;', body)
        self.assertNotIn('&#x27;', body)


class OrderAccessControlTests(TestCase):
    """Covers: the thank-you page is only visible to the person who placed
    the order (via session) or its logged-in owner — not to strangers who
    happen to know/guess the order number."""

    def setUp(self):
        self.product = Product.objects.create(name='Private Item', price=20, stock=10)

    def test_stranger_cannot_view_someone_elses_thank_you_page(self):
        self.client.post(reverse('cart:cart_add', args=[self.product.id]), {'quantity': 1, 'override': 'True'})
        resp = self.client.post(reverse('orders:checkout'), CHECKOUT_DATA, follow=True)
        order_number = Order.objects.latest('created_at').order_number

        stranger_client = self.client_class()
        resp = stranger_client.get(reverse('orders:thank_you', args=[order_number]), follow=True)
        self.assertTrue(any('/orders/track/' in url for url, code in resp.redirect_chain))
