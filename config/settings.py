"""
Django settings for Furni E-Commerce project.

Every value that differs between development and production (secret key,
debug flag, database, email/SMTP credentials, cache backend, etc.) is read
from environment variables — see `.env.example` for the full list and
instructions on how to fill in a real `.env` file.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Load variables from a .env file placed at the project root (same folder as manage.py).
# If no .env file exists, this is a no-op and the os.environ defaults below are used instead.
load_dotenv(BASE_DIR / '.env')


# ==========================================================
# Small helpers for reading typed values out of the environment
# ==========================================================
def env(key, default=None):
    return os.environ.get(key, default)


def env_bool(key, default=False):
    value = os.environ.get(key)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def env_int(key, default=None):
    value = os.environ.get(key)
    if value is None or value == '':
        return default
    return int(value)


def env_list(key, default=''):
    value = os.environ.get(key, default)
    return [item.strip() for item in value.split(',') if item.strip()]


# ==========================================================
# Core
# ==========================================================
SECRET_KEY = env('SECRET_KEY', 'django-insecure-CHANGE-THIS-SECRET-KEY-IN-PRODUCTION-abc123xyz987')

DEBUG = env_bool('DEBUG', True)

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', '*')

# ==========================================================
# Applications
# ==========================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',

    # Local apps
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'shop.apps.ShopConfig',
    'cart.apps.CartConfig',
    'orders.apps.OrdersConfig',
    'blog.apps.BlogConfig',
    'newsletter.apps.NewsletterConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shop.context_processors.categories_processor',
                'cart.context_processors.cart_processor',
                'core.context_processors.site_settings_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ==========================================================
# Database
# ==========================================================
# Defaults to SQLite (zero setup, great for development/demos).
# Set DB_ENGINE=postgres in .env to switch to PostgreSQL for production.
if env('DB_ENGINE', 'sqlite') == 'postgres':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', 'furni'),
            'USER': env('DB_USER', 'furni'),
            'PASSWORD': env('DB_PASSWORD', ''),
            'HOST': env('DB_HOST', 'localhost'),
            'PORT': env('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==========================================================
# Cache (used for login brute-force throttling)
# ==========================================================
# Defaults to Django's in-process LocMemCache (fine for a single dev server).
# Set REDIS_URL in .env to switch to Redis — required in production whenever
# you run more than one worker process, or the login-throttle counters won't
# be shared correctly between processes.
REDIS_URL = env('REDIS_URL', '')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'furni-throttle-cache',
        }
    }

# ==========================================================
# Password validation
# ==========================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==========================================================
# Internationalization
# ==========================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = env('TIME_ZONE', 'Africa/Cairo')
USE_I18N = True
USE_TZ = True

# ==========================================================
# Static & Media files
# ==========================================================
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================================
# Auth redirects
# ==========================================================
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'

# ==========================================================
# Messages framework -> map to Bootstrap classes
# ==========================================================
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ==========================================================
# Email — used to send OTP codes (login/register) and password resets
# ==========================================================
# Defaults to the console backend: OTP/reset emails are printed to the
# terminal running `manage.py runserver` instead of actually being sent —
# perfect for local development, no setup required.
#
# To send REAL emails (required in production), set EMAIL_BACKEND=smtp in
# .env and fill in EMAIL_HOST / EMAIL_HOST_USER / EMAIL_HOST_PASSWORD.
# See .env.example for a ready-to-edit Gmail example.
if env('EMAIL_BACKEND', 'console') == 'smtp':
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = env_int('EMAIL_PORT', 587)
    EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
    EMAIL_USE_SSL = env_bool('EMAIL_USE_SSL', False)
    EMAIL_HOST_USER = env('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', '')
    EMAIL_TIMEOUT = 10
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', 'Furni Store <no-reply@furni.local>')

# ==========================================================
# Site settings
# ==========================================================
SITE_NAME = env('SITE_NAME', 'Furni')
FREE_SHIPPING_THRESHOLD = env_int('FREE_SHIPPING_THRESHOLD', 300)
SHIPPING_COST = env_int('SHIPPING_COST', 25)
TAX_RATE = float(env('TAX_RATE', '0.0'))

# ==========================================================
# Session security
# ==========================================================
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 2 weeks
CSRF_COOKIE_HTTPONLY = False  # kept False so JS-driven AJAX calls can read the CSRF token
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# ==========================================================
# Production hardening (auto-enabled only when DEBUG = False)
# ==========================================================
if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
