# Deploying Furni for Free (No Credit Card, $0)

This guide deploys the exact project in this repo to **PythonAnywhere's free
"Beginner" plan** — the only genuinely free (not trial-credit, not
time-limited) Django hosting option that also gives you **persistent disk
storage**, which matters a lot for this project since it uses SQLite (a
file-based database) and stores uploaded product/blog images as real files.

## Why PythonAnywhere and not X?

| Platform | Free forever? | Credit card? | Files/DB persist? |
|---|---|---|---|
| **PythonAnywhere** | ✅ Yes | ❌ Not required | ✅ Yes (512MB disk) |
| Render free tier | ✅ Yes | ❌ Not required | ⚠️ Disk resets on every redeploy — your SQLite DB and uploaded images would be wiped |
| Railway | ❌ Trial credit only, then paid | Often required | — |
| Fly.io / AWS / GCP free tiers | ⚠️ Time-limited or usage-limited | ✅ Required | ✅ Yes |

Since this project's database and every uploaded image live as real files on
disk (not in an external managed database/storage service), a host that
wipes your disk on every deploy (like Render's free tier) will silently
delete your orders, products, and uploaded photos. PythonAnywhere doesn't do
that — your files stay exactly where you put them.

**The trade-off:** your site lives at `https://yourusername.pythonanywhere.com`
(no custom domain on the free plan), and outbound internet access is
restricted to a allowlist — the one exception that matters for us is that
**Gmail's SMTP servers are specifically allowlisted for free accounts**,
which lines up perfectly with the Gmail SMTP example already in
`.env.example`. Any other SMTP provider (SendGrid, Outlook, etc.) will
*not* work on the free plan — stick with Gmail SMTP, or leave
`EMAIL_BACKEND=console` and simply check the PythonAnywhere error log for
OTP codes.

---

## Step 1 — Create your free account

1. Go to **pythonanywhere.com** → **Pricing & signup** → **Create a Beginner account** (free, no card).
2. Confirm your email.

## Step 2 — Upload the project

Open a **Bash console** from your PythonAnywhere dashboard (`Consoles` tab
→ `Bash`), then either:

**Option A — you have this project on GitHub:**
```bash
git clone https://github.com/yourusername/furni_ecommerce.git
```

**Option B — you only have the zip file:**
1. Go to the `Files` tab, upload `furni_django_ecommerce.zip` to your home directory.
2. Back in the Bash console:
```bash
unzip furni_django_ecommerce.zip
```

Either way, you should now have `~/furni_ecommerce/` containing `manage.py`.

## Step 3 — Create a virtual environment and install dependencies

Still in the Bash console:
```bash
cd ~/furni_ecommerce
mkvirtualenv --python=/usr/bin/python3.10 furni-env
pip install -r requirements.txt
```
(`mkvirtualenv` automatically activates the new environment — you'll see
`(furni-env)` in your prompt.)

## Step 4 — Configure `.env` for production

Edit the existing `.env` file (Files tab, or `nano .env` in the console) so it looks like this:

```env
SECRET_KEY=paste-a-real-random-key-here
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com

# Leave as console to skip email setup (OTP codes appear in the error log instead),
# or fill in Gmail SMTP — the one provider that works on the free plan:
EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-address@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-gmail-app-password
DEFAULT_FROM_EMAIL=Furni Store <your-address@gmail.com>
```

Generate a real `SECRET_KEY` first:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

For the Gmail app password: turn on 2-Step Verification on the Gmail
account, then create an **App Password** at
`myaccount.google.com/apppasswords` — use that 16-character password, not
the normal Gmail password.

## Step 5 — Set up the database and static files

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```
Follow the prompts to create your real admin login (skip `seed_data` unless
you specifically want the demo products/blog posts — it's still there if
you do want a populated storefront to start from: `python manage.py seed_data`).

## Step 6 — Create the web app

1. Go to the **Web** tab → **Add a new web app**.
2. Choose **Manual configuration** (not the Django wizard — we already have a custom project layout).
3. Pick the same Python version you used for the virtualenv (3.10).
4. On the resulting configuration page, set:
   - **Virtualenv**: `/home/yourusername/.virtualenvs/furni-env`
   - **Source code**: `/home/yourusername/furni_ecommerce`

## Step 7 — Point the WSGI file at this project

Still on the Web tab, click the **WSGI configuration file** link. Delete
everything in it and replace with:

```python
import os
import sys

path = '/home/yourusername/furni_ecommerce'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```
(Replace `yourusername` with your actual PythonAnywhere username in both
this file and the Web tab paths above.)

## Step 8 — Map static and media files

Still on the Web tab, scroll to **Static files** and add two entries:

| URL | Directory |
|---|---|
| `/static/` | `/home/yourusername/furni_ecommerce/staticfiles` |
| `/media/` | `/home/yourusername/furni_ecommerce/media` |

This is what makes product images, CSS, and JS actually load — without it
the site will render with no styling and broken images.

## Step 9 — Go live

Click the big green **Reload** button at the top of the Web tab. Then visit
`https://yourusername.pythonanywhere.com` — the site should be live.

Log into `/admin/` with the superuser you created in Step 5 to add real
products, categories, and site settings.

---

## Free-tier limits worth knowing

- **512MB disk quota total** (code + database + all uploaded images). Fine
  for a real small storefront; keep an eye on it if you upload a lot of
  large product photos — compress images before uploading.
- **100 CPU-seconds/day** — plenty for a low-traffic site; a burst of
  visitors on a busy day could hit this, in which case the site briefly
  serves a "CPU limit reached" page until the daily quota resets.
- **Only Gmail SMTP works** for sending real email on the free plan (see
  Step 4). Any other provider's SMTP will time out.
- **No background task workers** — not an issue here, since this project
  doesn't use Celery or any background jobs.
- **Custom domains require a paid plan.** Your free URL is fixed at
  `yourusername.pythonanywhere.com`.

## After you make code changes

Whenever you edit the code (locally then re-upload, or `git pull` if you
used Option A in Step 2), reapply migrations/static files if needed, then
just hit **Reload** on the Web tab again — no redeploy pipeline to manage.
