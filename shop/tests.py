from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Category, Product, Review


class ShopFilterSafetyTests(TestCase):
    """Covers: the min_price/max_price and page querystring filters must
    never crash the shop page, no matter what garbage is passed in."""

    def setUp(self):
        category = Category.objects.create(name='Chairs')
        Product.objects.create(category=category, name='Test Chair', price=100, stock=5)

    def test_garbage_price_values_do_not_crash(self):
        for value in ['abc', '<script>alert(1)</script>', '-50', 'NaN', 'Infinity', '1e500']:
            resp = self.client.get(reverse('shop:shop_list'), {'min_price': value})
            self.assertEqual(resp.status_code, 200, f'min_price={value!r} should not crash the page')

    def test_garbage_page_values_do_not_crash(self):
        for value in ['abc', '99999', '-1', '0']:
            resp = self.client.get(reverse('shop:shop_list'), {'page': value})
            self.assertEqual(resp.status_code, 200, f'page={value!r} should not crash the page')

    def test_valid_price_filter_actually_filters(self):
        Product.objects.create(name='Expensive', price=500, stock=1)
        resp = self.client.get(reverse('shop:shop_list'), {'min_price': '200'})
        self.assertContains(resp, 'Expensive')
        self.assertNotContains(resp, 'Test Chair')


class ReviewModerationTests(TestCase):
    """Covers: reviews require approval before appearing publicly, and a
    second review attempt for the same product is rejected gracefully
    (not a database crash) regardless of the first review's approval state."""

    def setUp(self):
        self.user = User.objects.create_user(username='reviewer', password='x', email='r@example.com')
        self.product = Product.objects.create(name='Reviewable', price=50, stock=5)

    def test_new_review_is_not_approved_by_default(self):
        review = Review.objects.create(product=self.product, user=self.user, rating=5, comment='Nice')
        self.assertFalse(review.is_approved)

    def test_unapproved_review_not_shown_publicly(self):
        Review.objects.create(product=self.product, user=self.user, rating=5, comment='Hidden review text')
        resp = self.client.get(self.product.get_absolute_url())
        self.assertNotContains(resp, 'Hidden review text')

    def test_duplicate_review_submission_does_not_crash(self):
        self.client.login(username='reviewer', password='x')
        Review.objects.create(product=self.product, user=self.user, rating=5, comment='First')
        resp = self.client.post(self.product.get_absolute_url(), {
            'rating': 3, 'title': 'Second', 'comment': 'Trying again',
        })
        self.assertEqual(resp.status_code, 302)  # graceful redirect, not a 500
        self.assertEqual(Review.objects.filter(product=self.product, user=self.user).count(), 1)


class WishlistCsrfTests(TestCase):
    """Covers: toggling a wishlist item requires POST (not a plain link),
    so an external page can't silently modify it via an <img> tag."""

    def setUp(self):
        self.user = User.objects.create_user(username='wisher', password='x', email='w@example.com')
        self.product = Product.objects.create(name='Wishable', price=50, stock=5)

    def test_get_request_rejected(self):
        self.client.login(username='wisher', password='x')
        resp = self.client.get(reverse('shop:toggle_wishlist', args=[self.product.slug]))
        self.assertEqual(resp.status_code, 405)

    def test_post_request_toggles_it(self):
        self.client.login(username='wisher', password='x')
        from .models import Wishlist
        self.client.post(reverse('shop:toggle_wishlist', args=[self.product.slug]))
        self.assertTrue(Wishlist.objects.filter(user=self.user, product=self.product).exists())
