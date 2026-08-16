from django.test import TestCase
from django.urls import reverse

from .models import Subscriber
from .utils import generate_unsubscribe_token, verify_unsubscribe_token


class NewsletterTests(TestCase):
    def test_duplicate_subscription_does_not_crash(self):
        self.client.post(reverse('newsletter:subscribe'), {'email': 'dup@example.com', 'website': ''})
        resp = self.client.post(reverse('newsletter:subscribe'), {'email': 'dup@example.com', 'website': ''})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Subscriber.objects.filter(email='dup@example.com').count(), 1)

    def test_honeypot_blocks_bot_subscription(self):
        self.client.post(reverse('newsletter:subscribe'), {'email': 'bot@example.com', 'website': 'http://spam.com'})
        self.assertFalse(Subscriber.objects.filter(email='bot@example.com').exists())

    def test_unsubscribe_token_roundtrip(self):
        token = generate_unsubscribe_token('someone@example.com')
        self.assertEqual(verify_unsubscribe_token(token), 'someone@example.com')

    def test_unsubscribe_deactivates_subscriber(self):
        Subscriber.objects.create(email='leaving@example.com')
        token = generate_unsubscribe_token('leaving@example.com')
        self.client.get(reverse('newsletter:unsubscribe', args=[token]))
        sub = Subscriber.objects.get(email='leaving@example.com')
        self.assertFalse(sub.is_active)

    def test_invalid_token_does_not_crash(self):
        resp = self.client.get(reverse('newsletter:unsubscribe', args=['totally-fake-token']))
        self.assertEqual(resp.status_code, 200)
