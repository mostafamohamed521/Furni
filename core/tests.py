from django.test import TestCase
from django.urls import reverse


class PublicPagesRenderTests(TestCase):
    """Smoke test: every core public page renders successfully with no
    server error."""

    def test_public_pages_return_200(self):
        for name in ['core:home', 'core:about', 'core:services', 'core:contact',
                     'core:faq', 'core:terms', 'core:privacy']:
            resp = self.client.get(reverse(name))
            self.assertEqual(resp.status_code, 200, f'{name} should return 200')

    def test_contact_form_honeypot_blocks_bot(self):
        from .models import ContactMessage
        self.client.post(reverse('core:contact'), {
            'first_name': 'Bot', 'last_name': 'X', 'email': 'bot@example.com',
            'message': 'spam', 'website': 'http://spam.com',
        })
        self.assertFalse(ContactMessage.objects.filter(email='bot@example.com').exists())

    def test_sitemap_and_robots(self):
        self.assertEqual(self.client.get('/sitemap.xml').status_code, 200)
        self.assertEqual(self.client.get('/robots.txt').status_code, 200)
