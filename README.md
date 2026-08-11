# Furni — Full-Featured E-Commerce Furniture Store (Django)

A complete e-commerce web application built with Django, based on the original **Furni**
HTML/CSS template, fully converted into a dynamic store with an admin dashboard,
user accounts, shopping cart, order management, blog, reviews, wishlist, newsletter,
and a professional loading/welcome animation.

---

## 🧱 Project Structure (Separate Apps)

```
furni_ecommerce/
├── config/          # Main project settings (settings, urls, wsgi)
├── core/            # Home, About, Services, Contact, FAQ, Terms, Privacy, 404/500
├── accounts/        # Register / Login / Logout / Profile / Password reset
├── shop/            # Categories, Products, Reviews, Wishlist, Search
├── cart/            # Shopping cart (session-based)
├── orders/          # Checkout, Orders, Coupons, Order tracking
├── blog/            # Blog posts and comments
├── newsletter/       # Newsletter subscriptions
├── templates/        # All templates — organized per app
│   ├── base.html
│   ├── partials/
│   ├── core/ shop/ cart/ orders/ blog/ accounts/
├── static/
│   ├── css/ (original style.css + extra-style.css for animations)
│   ├── js/  (original custom.js + app.js for animations/interactions)
│   └── images/
└── media/            # Product/blog/avatar images uploaded via the admin
```

Every app has its own `models.py`, `views.py`, `urls.py`, `forms.py`, and `admin.py`,
following clean Django architecture — logic is fully decoupled from templates.

---

## ✨ Implemented Features

### For visitors / customers
- Home, About, Services, Blog, Contact — **every page is wired to a real database**
- Full shop with: category filtering, search, sorting (newest / price / name), pagination
- Product detail page: gallery, reviews, add a review, related products, add to cart with quantity
- Full shopping cart (add / update quantity / remove / clear)
- **Complete checkout**: billing address, optional different shipping address, coupon codes,
  automatic free shipping above a threshold, multiple payment methods
- Order confirmation ("Thank You") page with a unique order number
- User accounts: register / login / logout / edit profile / change password / forgot password
- Order history and per-order detail page
- **Guest order tracking** (order number + email — no login required)
- Wishlist
- Blog comments
- Newsletter signup from the footer on every page
- **FAQ page** and **Terms & Conditions / Privacy Policy** pages (editable from the admin)
- `sitemap.xml` and `robots.txt` for SEO
- **Loading animation (Preloader)** on every page load
- **Welcome overlay animation** shown once per browsing session
- Scroll-reveal animations, toast notifications for messages, fully responsive design

### For the admin (full Django admin dashboard at `/admin/`)
- Manage products, categories, extra product images, and stock
- Manage orders and update their status (Pending / Processing / Shipped / Delivered / Cancelled)
- Manage coupons, reviews, blog posts, team members, testimonials, services, contact messages
- Manage FAQs and legal pages (Terms & Conditions, Privacy Policy) without touching code
- Manage global site settings (address, phone, social links) from a single place

---

## ⚙️ Running Locally

```bash
cd furni_ecommerce
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data      # populates the store with demo data (products, categories, posts...)
python manage.py runserver
```

Then open: `http://127.0.0.1:8000/`

### Admin dashboard credentials (created automatically by seed_data)
```
URL:      /admin/
Username: admin
Password: admin12345
```
**⚠️ Change this password immediately in any real production environment.**

---

## 🔐 Security Hardening Actually Implemented in the Code

The accounts and orders flows were fully audited, and the following protections were added
(not just claims — every point below was actually tested):

| Protection | Details |
|---|---|
| **CSRF** | Every form (including the footer newsletter form) includes `{% csrf_token %}` — verified across the whole project |
| **Login brute-force protection** | After 5 failed attempts from the same IP, login is locked for 5 minutes (via Django's cache framework) |
| **Logout via POST only** | `/accounts/logout/` rejects GET requests (405) to prevent logging a user out via a malicious link |
| **Safe avatar uploads** | Profile pictures are actually validated (real file type via Pillow, 3MB max size, JPEG/PNG/WEBP only) — tested by uploading a `.php` file disguised as an image, which was correctly rejected |
| **Honeypot anti-bot fields** | Registration, contact, newsletter, and blog comment forms include a hidden field — if it's filled in (typical bot behavior), the submission is automatically rejected |
| **Order data protection** | The "Thank You" page (shown right after checkout) is only viewable by the order's owner (same session or logged-in account) — anyone else is redirected to the "Track Order" page, which requires the email used for the order |
| **Order access control (IDOR protection)** | Order history and order detail pages require `login_required` and are filtered by `user=request.user` — no one can view another customer's order by changing the number in the URL |
| **Password strength** | Minimum 8 characters + similarity check against user info + common-password check + rejects all-numeric passwords |
| **HTTP security headers** | `X-Frame-Options: DENY`, `SECURE_CONTENT_TYPE_NOSNIFF`, `SECURE_BROWSER_XSS_FILTER` are always enabled |
| **Auto-hardening on deploy** | When `DEBUG = False`, the following are enabled automatically: `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, and a full year of HSTS — no manual changes needed |
| **SQL Injection** | Not possible by design — every query goes through the Django ORM; there is no raw SQL anywhere in the project |
| **XSS** | Django templates auto-escape all variables by default; the only field using `|safe` is the content of the legal pages (Terms/Privacy), which is edited by a trusted admin only, never by end-user input |

### ⚠️ Important note about caching
The brute-force protection uses the default `LocMemCache`, which only works correctly on a
single-process development server. **In a real production environment with more than one
worker/process, you must switch to Redis** for the protection to work consistently across processes:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

The protections above are **in addition to** everything listed in the "Security notes before
deployment" section below — enabling HTTPS, a real `SECRET_KEY`, PostgreSQL, and integrating a
real payment gateway are still required before any real-world launch.

---

## 🔐 Security Notes Before Deployment (Production)

1. Change `SECRET_KEY` in `config/settings.py` and load it from an environment variable.
2. Set `DEBUG = False` and configure `ALLOWED_HOSTS` precisely.
3. Use a production database (PostgreSQL) instead of SQLite.
4. Enable HTTPS and use `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`
   (these are already auto-enabled when `DEBUG = False`, see above).
5. Integrate a real payment gateway (Stripe/PayPal) instead of the default "Cash on Delivery".
6. Use a real email service (SMTP) instead of `console.EmailBackend`.
7. Run `python manage.py collectstatic` and serve static files via a CDN or Nginx.
8. Switch the cache backend to Redis (see the caching note above) so login-throttling works
   correctly across multiple worker processes.

---

## 🧪 Actually Smoke-Tested

Automated tests were run covering: every page (200 OK), new user registration, adding a
product to the cart, a full checkout flow (Checkout → Order created), submitting a product
review, toggling the wishlist, viewing order history, newsletter signup, sending a contact
message, guest order tracking, the FAQ/Terms/Privacy pages, `sitemap.xml`/`robots.txt`, and
the admin dashboard — **everything works with zero errors.** The security hardening listed
above (brute-force lockout, malicious file upload rejection, honeypot bot-blocking, and
order-ownership checks) was also verified with dedicated test scripts.

---

Built as an extension of the **Furni** template (Untree.co) — fully converted into a
professional Django e-commerce platform.