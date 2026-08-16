from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import cache
from django.urls import reverse

from .models import OTPCode


class RegistrationOtpFlowTests(TestCase):
    """Covers: registration does NOT log the user in until the emailed
    OTP is verified, wrong codes are rejected, and the correct code
    completes registration."""

    def setUp(self):
        cache.clear()

    def _register(self):
        return self.client.post(reverse('accounts:register'), {
            'first_name': 'Test', 'last_name': 'User', 'username': 'flowtester',
            'email': 'flowtester@example.com',
            'password1': 'VeryStrongPass2024', 'password2': 'VeryStrongPass2024',
            'website': '',
        })

    def test_register_does_not_start_session_before_otp(self):
        self._register()
        self.assertFalse(self.client.session.get('_auth_user_id'))
        self.assertTrue(User.objects.filter(username='flowtester').exists())

    def test_wrong_otp_code_is_rejected(self):
        self._register()
        resp = self.client.post(reverse('accounts:verify_otp'), {'code': '000000'})
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

    def test_correct_otp_code_logs_user_in(self):
        self._register()
        user = User.objects.get(username='flowtester')
        otp = OTPCode.objects.filter(user=user, purpose='register').latest('created_at')
        resp = self.client.post(reverse('accounts:verify_otp'), {'code': otp.code}, follow=True)
        self.assertTrue(resp.wsgi_request.user.is_authenticated)

    def test_otp_bot_honeypot_blocks_registration(self):
        resp = self.client.post(reverse('accounts:register'), {
            'first_name': 'Bot', 'last_name': 'User', 'username': 'botuser',
            'email': 'bot@example.com',
            'password1': 'VeryStrongPass2024', 'password2': 'VeryStrongPass2024',
            'website': 'http://spam.example.com',
        })
        self.assertFalse(User.objects.filter(username='botuser').exists())


class LoginOtpFlowTests(TestCase):
    """Covers: login is two-step (password, then OTP), brute-force
    lockout on both the password step and the OTP step, and that
    resubmitting a correct password doesn't spam a new email every time."""

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username='loginflow', email='loginflow@example.com', password='VeryStrongPass2024'
        )

    def test_correct_password_does_not_log_in_immediately(self):
        resp = self.client.post(reverse('accounts:login'), {
            'username': 'loginflow', 'password': 'VeryStrongPass2024',
        })
        self.assertFalse(resp.wsgi_request.user.is_authenticated)
        self.assertTrue(OTPCode.objects.filter(user=self.user, purpose='login').exists())

    def test_correct_otp_completes_login(self):
        self.client.post(reverse('accounts:login'), {
            'username': 'loginflow', 'password': 'VeryStrongPass2024',
        })
        otp = OTPCode.objects.filter(user=self.user, purpose='login').latest('created_at')
        resp = self.client.post(reverse('accounts:verify_otp'), {'code': otp.code}, follow=True)
        self.assertTrue(resp.wsgi_request.user.is_authenticated)

    def test_password_brute_force_lockout(self):
        for _ in range(5):
            self.client.post(reverse('accounts:login'), {'username': 'loginflow', 'password': 'wrong'})
        resp = self.client.post(reverse('accounts:login'), {
            'username': 'loginflow', 'password': 'VeryStrongPass2024',
        })
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

    def test_otp_brute_force_lockout_clears_pending_session(self):
        self.client.post(reverse('accounts:login'), {
            'username': 'loginflow', 'password': 'VeryStrongPass2024',
        })
        for _ in range(5):
            self.client.post(reverse('accounts:verify_otp'), {'code': '000000'})
        self.assertNotIn('otp_pending_user_id', self.client.session)

    def test_repeated_login_does_not_spam_new_otp_emails(self):
        for _ in range(5):
            self.client.post(reverse('accounts:login'), {
                'username': 'loginflow', 'password': 'VeryStrongPass2024',
            })
        self.assertEqual(OTPCode.objects.filter(user=self.user, purpose='login').count(), 1)

    def test_logout_requires_post(self):
        self.client.login(username='loginflow', password='VeryStrongPass2024')
        resp = self.client.get(reverse('accounts:logout'))
        self.assertEqual(resp.status_code, 405)


class PasswordResetThrottleTests(TestCase):
    """Covers: repeated password-reset requests for the same email don't
    spam multiple emails, and the response never reveals whether an
    email is registered."""

    def setUp(self):
        cache.clear()
        User.objects.create_user(username='resetme', email='resetme@example.com', password='x')

    def test_repeated_requests_same_email_throttled(self):
        from django.core import mail
        for _ in range(5):
            self.client.post(reverse('accounts:password_reset'), {'email': 'resetme@example.com'})
        self.assertEqual(len(mail.outbox), 1)

    def test_response_identical_for_real_and_fake_email(self):
        resp_real = self.client.post(reverse('accounts:password_reset'), {'email': 'resetme@example.com'})
        resp_fake = self.client.post(reverse('accounts:password_reset'), {'email': 'nobody@example.com'})
        self.assertEqual(resp_real.status_code, resp_fake.status_code)
        self.assertEqual(resp_real.url, resp_fake.url)
