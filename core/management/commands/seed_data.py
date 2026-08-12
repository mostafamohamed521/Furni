import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.files import File
from django.contrib.auth.models import User
from django.conf import settings

from shop.models import Category, Product
from core.models import Testimonial, TeamMember, Service, SiteSetting, FAQ, LegalPage
from blog.models import BlogCategory, Post
from orders.models import Coupon

IMAGES_DIR = settings.BASE_DIR / 'static' / 'images'


def get_image_file(name):
    path = IMAGES_DIR / name
    if path.exists():
        return File(open(path, 'rb'), name=name)
    return None


class Command(BaseCommand):
    help = 'Seed the database with demo data for the Furni store.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # --- Superuser ---
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@furni.local', 'admin12345')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin / admin12345'))

        # --- Categories ---
        categories_data = [
            ('Chairs', 'Comfortable and stylish chairs for every room.'),
            ('Sofas', 'Premium sofas crafted for comfort and elegance.'),
            ('Tables', 'Modern tables for living, dining, and office.'),
            ('Lighting', 'Ambient lighting solutions for a cozy home.'),
            ('Decor', 'Beautiful decor pieces to complete your space.'),
            ('Storage', 'Functional storage solutions with style.'),
        ]
        categories = {}
        for i, (name, desc) in enumerate(categories_data):
            cat, _ = Category.objects.get_or_create(name=name, defaults={'description': desc, 'order': i})
            categories[name] = cat
        self.stdout.write(self.style.SUCCESS(f'Categories: {Category.objects.count()}'))

        # --- Products ---
        products_data = [
            ('Nordic Chair', 'Chairs', 50.00, None, 'product-1.png', 'A minimalist Nordic-style chair with solid wood legs and premium upholstery.'),
            ('Kruzo Aero Chair', 'Chairs', 78.00, 95.00, 'product-2.png', 'Ergonomic aero chair designed for comfort during long working hours.'),
            ('Ergonomic Chair', 'Chairs', 43.00, None, 'product-3.png', 'A supportive ergonomic chair ideal for home offices.'),
            ('Nordic Lounge Chair', 'Chairs', 65.00, None, 'product-1.png', 'Relax in style with this Nordic lounge chair.'),
            ('Classic Sofa 3-Seater', 'Sofas', 320.00, 380.00, 'couch.png', 'A spacious three-seater sofa with soft cushions and durable fabric.'),
            ('Modern Sectional Sofa', 'Sofas', 540.00, None, 'sofa.png', 'Statement sectional sofa perfect for large living rooms.'),
            ('Compact Loveseat', 'Sofas', 210.00, None, 'couch.png', 'A cozy loveseat that fits perfectly in smaller spaces.'),
            ('Round Coffee Table', 'Tables', 89.00, 110.00, 'bowl-2.png', 'Elegant round coffee table with a walnut finish.'),
            ('Oak Dining Table', 'Tables', 260.00, None, 'bowl-3.png', 'Solid oak dining table that seats up to six people.'),
            ('Minimalist Side Table', 'Tables', 45.00, None, 'bowl-2.png', 'A simple yet stylish side table for any corner.'),
            ('Pendant Lamp', 'Lighting', 38.00, None, 'product-2.png', 'Modern pendant lamp that adds warm ambient lighting.'),
            ('Floor Lamp Classic', 'Lighting', 72.00, 88.00, 'product-3.png', 'Tall floor lamp with a fabric shade and wooden base.'),
            ('Ceramic Vase Set', 'Decor', 28.00, None, 'bowl-2.png', 'Set of handcrafted ceramic vases to decorate your shelves.'),
            ('Wall Art Canvas', 'Decor', 55.00, None, 'bowl-3.png', 'Abstract wall art canvas to bring color into your room.'),
            ('Storage Cabinet', 'Storage', 150.00, 175.00, 'product-1.png', 'Spacious storage cabinet with adjustable shelves.'),
            ('Bookshelf Ladder', 'Storage', 98.00, None, 'product-2.png', 'A stylish ladder bookshelf for books and decor items.'),
        ]

        created_products = []
        for i, (name, cat_name, price, old_price, img, desc) in enumerate(products_data):
            if Product.objects.filter(name=name).exists():
                created_products.append(Product.objects.get(name=name))
                continue
            product = Product(
                category=categories.get(cat_name),
                name=name,
                short_description=desc[:100],
                description=desc,
                price=Decimal(str(price)),
                old_price=Decimal(str(old_price)) if old_price else None,
                stock=random.randint(5, 40),
                is_active=True,
                is_featured=i < 4,
                is_popular=4 <= i < 7,
                material=random.choice(['Solid Wood', 'Oak', 'Velvet Fabric', 'Metal & Glass', 'Rattan']),
                color=random.choice(['Beige', 'Walnut', 'Charcoal', 'White', 'Natural']),
            )
            img_file = get_image_file(img)
            if img_file:
                product.image.save(img, img_file, save=False)
            product.save()
            created_products.append(product)
        self.stdout.write(self.style.SUCCESS(f'Products: {Product.objects.count()}'))

        # --- Testimonials ---
        testimonials_data = [
            ('Maria Jones', 'CEO, Co-Founder, XYZ Inc.', 'Furni transformed our office into a place people actually enjoy working in. The quality is outstanding.', 'person-1.png'),
            ('Robert Fox', 'Interior Designer', 'I always recommend Furni to my clients — the craftsmanship and design sense are unmatched.', 'person_1.jpg'),
            ('Kristin Watson', 'Homeowner', 'From ordering to delivery, everything was smooth. My living room has never looked better!', 'person_2.jpg'),
        ]
        for name, position, content, img in testimonials_data:
            if not Testimonial.objects.filter(name=name).exists():
                t = Testimonial(name=name, position=position, content=content)
                img_file = get_image_file(img)
                if img_file:
                    t.photo.save(img, img_file, save=False)
                t.save()

        # --- Team ---
        team_data = [
            ('Alicia Harper', 'Founder & Creative Director', 'person_1.jpg'),
            ('Omar Khalid', 'Lead Interior Designer', 'person_2.jpg'),
            ('Sarah Ahmed', 'Head of Operations', 'person_3.jpg'),
            ('Joseph Adel', 'Customer Experience Lead', 'person_4.jpg'),
        ]
        for i, (name, role, img) in enumerate(team_data):
            member, _ = TeamMember.objects.update_or_create(role=role, defaults={'name': name, 'order': i})
            if not member.photo:
                img_file = get_image_file(img)
                if img_file:
                    member.photo.save(img, img_file, save=True)

        # --- Services ---
        services_data = [
            ('Interior Design Consultation', 'fa-solid fa-couch', 'Personalized interior design consultations that match your taste and space, with a team of experts.'),
            ('Fast Delivery & Installation', 'fa-solid fa-truck', 'Fast delivery and professional installation for every piece, often on the same day.'),
            ('Hassle-Free Returns', 'fa-solid fa-arrows-rotate', 'A flexible return policy within 14 days of delivery, with no hassle.'),
            ('Custom Furniture Making', 'fa-solid fa-hammer', 'Custom-made furniture pieces built to your exact measurements and preferences.'),
            ('24/7 Customer Support', 'fa-solid fa-headset', 'A support team available around the clock to answer all your questions.'),
            ('Home Styling Service', 'fa-solid fa-palette', 'A complete styling service to help you choose the right colors and pieces.'),
        ]
        for i, (title, icon, desc) in enumerate(services_data):
            Service.objects.update_or_create(title=title, defaults={'icon_class': icon, 'description': desc, 'order': i})

        # --- Blog ---
        blog_cat, _ = BlogCategory.objects.get_or_create(name='Home Tips')
        admin_user = User.objects.filter(username='admin').first()
        posts_data = [
            ('First Time Home Owner Ideas', 'post-1.jpg', 'Tips and tricks for decorating your first home on a budget, from choosing colors to arranging furniture.'),
            ('How To Keep Your Furniture Clean', 'post-2.jpg', 'A practical guide on maintaining and cleaning different types of furniture materials.'),
            ('Small Space Furniture Apartment Ideas', 'post-3.jpg', 'Smart furniture choices that maximize small living spaces without compromising style.'),
        ]
        for title, img, content in posts_data:
            if not Post.objects.filter(title=title).exists():
                p = Post(title=title, author=admin_user, category=blog_cat, excerpt=content[:120], content=content * 3)
                img_file = get_image_file(img)
                if img_file:
                    p.image.save(img, img_file, save=False)
                p.save()

        # --- Coupon ---
        Coupon.objects.get_or_create(code='FURNI10', defaults={'discount_percent': 10, 'active': True})
        Coupon.objects.get_or_create(code='WELCOME20', defaults={'discount_percent': 20, 'active': True})

        # --- FAQs ---
        faqs_data = [
            ('What are your delivery times?', 'Delivery usually takes 3 to 7 business days depending on your location. An estimated delivery time is shown at checkout.'),
            ('Can I return a product?', 'Yes, you can return any product within 14 days of delivery as long as it is in its original condition.'),
            ('Do you offer free shipping?', 'Yes, shipping is free on all orders over $300; otherwise a flat shipping fee applies.'),
            ('How can I track my order?', 'You can track your order from the "Track Order" page using your order number and email, or from "My Orders" if you have an account.'),
            ('What payment methods do you accept?', 'We accept Cash on Delivery, Direct Bank Transfer, and PayPal.'),
            ('Can I cancel or modify my order?', 'Please contact us as soon as you place your order to modify or cancel it before it ships.'),
        ]
        for i, (q, a) in enumerate(faqs_data):
            FAQ.objects.update_or_create(question=q, defaults={'answer': a, 'order': i})

        # --- Legal pages ---
        LegalPage.objects.update_or_create(page_type='terms', defaults={
            'title': 'Terms & Conditions',
            'content': (
                '<h4>1. Introduction</h4>'
                '<p>By using the Furni website, you agree to be bound by the following terms and conditions. '
                'Please read them carefully before making a purchase.</p>'
                '<h4>2. Orders & Payment</h4>'
                '<p>An order is confirmed once billing and shipping details have been correctly completed. '
                'Displayed prices include all applicable taxes unless otherwise stated.</p>'
                '<h4>3. Shipping & Delivery</h4>'
                '<p>We aim to deliver orders within the stated timeframe; delivery times may vary depending on '
                'location and circumstances beyond our control.</p>'
                '<h4>4. Returns & Exchanges</h4>'
                '<p>Customers may return a product within 14 days of delivery, provided it is unused and in its '
                'original condition.</p>'
                '<h4>5. Intellectual Property</h4>'
                '<p>All content on this website (text, images, designs) is the exclusive property of Furni and '
                'may not be used without prior permission.</p>'
            ),
        })
        LegalPage.objects.update_or_create(page_type='privacy', defaults={
            'title': 'Privacy Policy',
            'content': (
                '<h4>1. Information We Collect</h4>'
                '<p>We collect information you provide directly, such as your name, email, phone number, and '
                'shipping address, when you create an account or place an order.</p>'
                '<h4>2. How We Use Your Information</h4>'
                '<p>We use your data to process orders, improve your shopping experience, and communicate with '
                'you about your orders and our offers (if you have opted in).</p>'
                '<h4>3. Data Protection</h4>'
                '<p>We take reasonable security measures to protect your data from unauthorized access, use, or '
                'disclosure.</p>'
                '<h4>4. Sharing Your Data</h4>'
                '<p>We do not share your personal data with third parties except as necessary to complete '
                'shipping and payment.</p>'
                '<h4>5. Your Rights</h4>'
                '<p>You may request access to, correction of, or deletion of your data at any time by contacting us.</p>'
            ),
        })

        # --- Site settings ---
        SiteSetting.load()

        self.stdout.write(self.style.SUCCESS('✔ Seed data created successfully.'))
