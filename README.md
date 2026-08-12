# Furni — Full-Featured E-Commerce Furniture Store (Django)

A complete e-commerce web application built with Django, based on the original **Furni**
HTML/CSS template, fully converted into a dynamic store with an admin dashboard,
user accounts (with email OTP two-factor verification), shopping cart, order management,
blog, reviews, wishlist, newsletter, and a brand-consistent one-time loading animation.

---

## 🧱 Project Structure (Separate Apps)

```
furni_ecommerce/
├── config/          # Main project settings (settings, urls, wsgi)
├── core/            # Home, About, Services, Contact, FAQ, Terms, Privacy, 404/500
├── accounts/        # Register / Login / OTP verification / Profile / Password reset
├── shop/            # Categories, Products, Reviews, Wishlist, Search
├── cart/            # Shopping cart (session-based)
├── orders/          # Checkout, Orders, Coupons, Order tracking
├── blog/            # Blog posts and comments
├── newsletter/       # Newsletter subscriptions
├── templates/        # All templates — organized per app
│   ├── base.html
│   ├── partials/
│   ├── core/ shop/ cart/ orders/ blog/ accounts/ registration/
├── static/
│   ├── css/ (original style.css + extra-style.css for the on-brand entrance animation)
│   ├── js/  (original custom.js + app.js for the entrance animation/interactions)
│   └── images/
└── media/            # Product/blog/avatar images uploaded via the admin
```

Every app has its own `models.py`, `views.py`, `urls.py`, `forms.py`, and `admin.py`,
following clean Django architecture — logic is fully decoupled from templates.

The entire site — UI text, form labels, admin-facing messages, and all demo content
seeded by `seed_data` — is in **English**.

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
- **Two-factor account security (email OTP)** — see the dedicated section below
- User accounts: register / login / logout / edit profile / change password / forgot password
- Order history and per-order detail page
- **Guest order tracking** (order number + email — no login required)
- Wishlist
- Blog comments
- Newsletter signup from the footer on every page
- **FAQ page** and **Terms & Conditions / Privacy Policy** pages (editable from the admin)
- `sitemap.xml` and `robots.txt` for SEO
- **One-time entrance animation** (loading screen + welcome overlay) — shown once per
  browsing session, not on every page (see details below)
- Scroll-reveal animations, toast notifications for messages, fully responsive design

### For the admin (full Django admin dashboard at `/admin/`)
- Manage products, categories, extra product images, and stock
- Manage orders and update their status (Pending / Processing / Shipped / Delivered / Cancelled)
- Manage coupons, reviews, blog posts, team members, testimonials, services, contact messages
- Manage FAQs and legal pages (Terms & Conditions, Privacy Policy) without touching code
- Manage global site settings (address, phone, social links) from a single place
- Read-only visibility into issued OTP codes (for support/debugging)

---

## ⚙️ Environment Configuration (`.env`)

Every setting that differs between your machine and a real server — the secret key, debug
flag, database, and (most importantly) **how OTP emails actually get sent** — now lives in
a `.env` file at the project root, not hardcoded in `settings.py`.

- **`.env`** — a ready-to-run development configuration is already included in this
  download, so `python manage.py runserver` works immediately with zero setup.
- **`.env.example`** — the full reference with every available variable, explained, plus
  copy-paste-ready SMTP examples (Gmail, Outlook, SendGrid, etc.) for production.

To start your own environment from scratch:
```bash
cp .env.example .env
# then edit .env with a real editor
```

### How does the OTP code actually get sent?

It depends on one variable, `EMAIL_BACKEND`, in `.env`:

**In development (default — `EMAIL_BACKEND=console`, or the variable simply left unset)**
No real email is sent. The OTP code is printed straight to the terminal where
`python manage.py runserver` is running. After registering or logging in, just look at
that terminal — you'll see the full email text including the 6-digit code.

**In production (`EMAIL_BACKEND=smtp`)**
Real emails are sent through the SMTP server you configure. You need 5 more variables in
`.env`:
```env
EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-address@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=Furni Store <your-address@gmail.com>
```
`.env.example` has step-by-step instructions for getting a Gmail "App Password" (the
16-character password you use instead of your normal Gmail password when 2-Step
Verification is on), plus the host/port for Outlook, Yahoo, SendGrid, and similar
providers — any SMTP provider (Mailgun, Amazon SES, Postmark, etc.) works the same way,
just with different host/port/credentials.

### What else can `.env` control?

| Variable | What it does | Default |
|---|---|---|
| `SECRET_KEY` | Django's cryptographic secret key | insecure placeholder (change for production) |
| `DEBUG` | Debug mode — verbose errors, relaxed security | `True` |
| `ALLOWED_HOSTS` | Comma-separated list of domains allowed to serve the site | `*` |
| `DB_ENGINE` | `sqlite` (default) or `postgres` for production | `sqlite` |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | PostgreSQL connection details (only used when `DB_ENGINE=postgres`) | — |
| `REDIS_URL` | Switches the login-throttle cache from in-memory to Redis (needed with multiple workers) | unset → in-memory cache |
| `SITE_NAME`, `FREE_SHIPPING_THRESHOLD`, `SHIPPING_COST`, `TAX_RATE`, `TIME_ZONE` | Store-wide business settings | see `.env.example` |

Setting `DEBUG=False` also **automatically** turns on `SECURE_SSL_REDIRECT`,
`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, and a full year of HSTS — no separate
variable needed for those.

All of the above was verified by actually swapping `.env` between a dev config and a full
production-style config (SMTP + PostgreSQL + Redis) and confirming Django picked up every
value correctly.

---

## 🔑 Email OTP Verification (Login & Register)

Both registration and login now require a **6-digit one-time code sent by email** in
addition to the password — a simple two-factor flow with no third-party service required:

**Registration flow**
1. The person fills in the sign-up form.
2. The account is created, but **no session is started yet**.
3. A 6-digit code is generated and emailed to them (valid for 10 minutes).
4. They're taken to a "Verify Your Identity" page with a 6-box code input (auto-advance,
   backspace, and paste-friendly).
5. Once the correct code is entered, they are logged in automatically.

**Login flow**
1. Username + password are checked as normal.
2. If correct, the session is **not** started yet either — a fresh 6-digit code is emailed.
3. They confirm the code on the same verification page before the session actually begins.

**Extra details**
- A **resend** button is available with a 30-second cooldown to prevent spam.
- A **cancel** link clears the pending verification and returns to the login page.
- Codes expire after 10 minutes and are single-use (verifying invalidates all older
  outstanding codes for that purpose).
- Login attempts are still rate-limited (5 failed attempts → 5-minute lockout) *before*
  OTP is even reached, so brute-forcing the password is blocked at that stage too.

### ⚠️ Development note: where do the codes go?
By default `.env` sets `EMAIL_BACKEND=console`, so in development the OTP email is **not
actually sent** — it's printed straight to the terminal/console where `manage.py runserver`
is running. Just check that terminal output for the 6-digit code after registering or
logging in. See the "Environment Configuration" section above for exactly how to switch to
real SMTP email delivery.

---

## ⚙️ Running Locally

```bash
cd furni_ecommerce
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

pip install -r requirements.txt

# .env is already included with working development defaults — no edits needed to start.
python manage.py migrate
python manage.py seed_data      # populates the store with demo data (products, categories, posts...)
python manage.py runserver
```

Then open: `http://127.0.0.1:8000/`

**Remember:** after registering or logging in, check your terminal for the OTP code
(see the note above).

### Admin dashboard credentials (created automatically by seed_data)
```
URL:      /admin/
Username: admin
Password: admin12345
```
**⚠️ Change this password immediately in any real production environment.**

---

## 🎨 Brand-Consistent Entrance Animation

The loading screen and welcome overlay now use the site's actual brand colors
(`#3b5d50` dark green + `#f9bf29` gold, taken directly from `style.css`) instead of an
unrelated palette, so the very first impression matches the rest of the site.

More importantly: this animation is now a **true one-time entrance experience**.
A tiny synchronous script in `<head>` checks `sessionStorage` before anything else
renders — if the visitor has already seen it this browsing session, the loading
screen and welcome overlay are never shown again (not even in the DOM), so navigating
between pages is instant with zero "loading" flicker. It only reappears if the person
closes the tab and starts a new browsing session.

Inner pages (About, Shop, Cart, Checkout, FAQ, etc.) also use a more compact hero
section (`.hero-inner`) and tighter section spacing (`.tight-section`) instead of the
large, mostly-empty hero designed for the homepage, so pages feel purposefully laid
out rather than padded with empty space.

---

## 🔐 Security Hardening Actually Implemented in the Code

The accounts and orders flows were fully audited, and the following protections were added
(not just claims — every point below was actually tested):

| Protection | Details |
|---|---|
| **Two-factor login/register (OTP)** | See the dedicated section above — a stolen password alone is not enough to log in |
| **CSRF** | Every form (including the footer newsletter form) includes `{% csrf_token %}` — verified across the whole project |
| **Login brute-force protection** | After 5 failed attempts from the same IP, login is locked for 5 minutes (via Django's cache framework), evaluated before OTP is even reached |
| **Logout via POST only** | `/accounts/logout/` rejects GET requests (405) to prevent logging a user out via a malicious link |
| **Safe avatar uploads** | Profile pictures are actually validated (real file type via Pillow, 3MB max size, JPEG/PNG/WEBP only) — tested by uploading a `.php` file disguised as an image, which was correctly rejected |
| **Honeypot anti-bot fields** | Registration, contact, newsletter, and blog comment forms include a hidden field — if it's filled in (typical bot behavior), the submission is automatically rejected |
| **Order data protection** | The "Thank You" page (shown right after checkout) is only viewable by the order's owner (same session or logged-in account) — anyone else is redirected to the "Track Order" page, which requires the email used for the order |
| **Order access control (IDOR protection)** | Order history and order detail pages require `login_required` and are filtered by `user=request.user` — no one can view another customer's order by changing the number in the URL |
| **Password strength** | Minimum 8 characters + similarity check against user info + common-password check + rejects all-numeric passwords |
| **HTTP security headers** | `X-Frame-Options: DENY`, `SECURE_CONTENT_TYPE_NOSNIFF`, `SECURE_BROWSER_XSS_FILTER` are always enabled |
| **Auto-hardening on deploy** | When `DEBUG = False`, the following are enabled automatically: `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, and a full year of HSTS — no manual changes needed |
| **SQL Injection** | Not possible by design — every query goes through the Django ORM; there is no raw SQL anywhere in the project |
| **XSS** | Django templates auto-escape all variables by default; the only field using `\|safe` is the content of the legal pages (Terms/Privacy), which is edited by a trusted admin only, never by end-user input |

### ⚠️ Important note about caching
The brute-force protection uses the default `LocMemCache`, which only works correctly on a
single-process development server. **In a real production environment with more than one
worker/process, you must set `REDIS_URL` in `.env`** for the protection to work consistently
across processes:
```env
REDIS_URL=redis://127.0.0.1:6379/1
```

The protections above are **in addition to** everything listed in the "Security notes before
deployment" section below — enabling HTTPS, a real `SECRET_KEY`, PostgreSQL, and integrating a
real payment gateway are still required before any real-world launch.

---

## 🔐 Security Notes Before Deployment (Production)

1. In `.env`, set a real `SECRET_KEY` (generate one — see `.env.example`) and set `DEBUG=False`.
2. Set `ALLOWED_HOSTS` in `.env` to your real domain(s), not `*`.
3. Set `DB_ENGINE=postgres` in `.env` and fill in the connection details (see `.env.example`)
   instead of using SQLite.
4. HTTPS enforcement (`SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`)
   is already auto-enabled the moment `DEBUG=False` — no extra step needed, just make sure
   your server actually terminates HTTPS.
5. Integrate a real payment gateway (Stripe/PayPal) instead of the default "Cash on Delivery".
6. Set `EMAIL_BACKEND=smtp` in `.env` with real SMTP credentials — required for OTP codes
   and password-reset emails to actually reach users' inboxes in production.
7. Run `python manage.py collectstatic` and serve static files via a CDN or Nginx.
8. Set `REDIS_URL` in `.env` (see `.env.example`) so login-throttling works correctly
   across multiple worker processes.

---

## 🧪 Actually Smoke-Tested

Automated tests were run covering: every page (200 OK), new user registration through the
full OTP verification flow, login through the full OTP verification flow (including wrong
codes being rejected and the resend cooldown), adding a product to the cart, a full checkout
flow (Checkout → Order created), submitting a product review, toggling the wishlist, viewing
order history, newsletter signup, sending a contact message, guest order tracking, the
FAQ/Terms/Privacy pages, `sitemap.xml`/`robots.txt`, and the admin dashboard —
**everything works with zero errors.** A final full-project scan also confirmed there is
no leftover non-English text anywhere in the codebase.

---

Built as an extension of the **Furni** template (Untree.co) — fully converted into a
professional Django e-commerce platform.
