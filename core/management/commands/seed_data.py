import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.files import File
from django.contrib.auth.models import User
from django.conf import settings
import os

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
            ('Aliaa Hassan', 'Founder & Creative Director', 'person_1.jpg'),
            ('Omar Khaled', 'Lead Interior Designer', 'person_2.jpg'),
            ('Sara Ahmed', 'Head of Operations', 'person_3.jpg'),
            ('Youssef Adel', 'Customer Experience Lead', 'person_4.jpg'),
        ]
        for i, (name, role, img) in enumerate(team_data):
            if not TeamMember.objects.filter(name=name).exists():
                m = TeamMember(name=name, role=role, order=i)
                img_file = get_image_file(img)
                if img_file:
                    m.photo.save(img, img_file, save=False)
                m.save()

        # --- Services ---
        services_data = [
            ('Interior Design Consultation', 'fa-solid fa-couch', 'استشارات تصميم داخلي مخصصة تناسب ذوقك ومساحتك مع فريق من الخبراء.'),
            ('Fast Delivery & Installation', 'fa-solid fa-truck', 'توصيل سريع وتركيب احترافي لجميع القطع في نفس اليوم.'),
            ('Hassle-Free Returns', 'fa-solid fa-arrows-rotate', 'سياسة استرجاع مرنة خلال 14 يوم من الاستلام بدون تعقيد.'),
            ('Custom Furniture Making', 'fa-solid fa-hammer', 'تصنيع قطع أثاث مخصصة حسب المقاسات والتفضيلات الخاصة بك.'),
            ('24/7 Customer Support', 'fa-solid fa-headset', 'فريق دعم متواجد على مدار الساعة للإجابة عن جميع استفساراتك.'),
            ('Home Styling Service', 'fa-solid fa-palette', 'خدمة تنسيق كاملة لمساعدتك على اختيار الألوان والقطع المناسبة.'),
        ]
        for i, (title, icon, desc) in enumerate(services_data):
            Service.objects.get_or_create(title=title, defaults={'icon_class': icon, 'description': desc, 'order': i})

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
            ('What are your delivery times?', 'يستغرق التوصيل عادة من 3 إلى 7 أيام عمل حسب موقعك، وتظهر مدة التوصيل التقديرية عند إتمام الطلب.'),
            ('Can I return a product?', 'نعم، يمكنك إرجاع أي منتج خلال 14 يوماً من الاستلام بشرط أن يكون بحالته الأصلية.'),
            ('Do you offer free shipping?', 'نعم، الشحن مجاني لجميع الطلبات التي تتجاوز 300$، وإلا تُضاف رسوم شحن ثابتة.'),
            ('How can I track my order?', 'يمكنك تتبع طلبك من صفحة "Track Order" باستخدام رقم الطلب والبريد الإلكتروني، أو من صفحة "My Orders" إذا كان لديك حساب.'),
            ('What payment methods do you accept?', 'نقبل الدفع عند الاستلام (Cash on Delivery)، التحويل البنكي المباشر، وPayPal.'),
            ('Can I cancel or modify my order?', 'يمكنك التواصل معنا فور إتمام الطلب لتعديله أو إلغائه قبل شحنه.'),
        ]
        for i, (q, a) in enumerate(faqs_data):
            FAQ.objects.get_or_create(question=q, defaults={'answer': a, 'order': i})

        # --- Legal pages ---
        LegalPage.objects.get_or_create(page_type='terms', defaults={
            'title': 'Terms & Conditions',
            'content': (
                '<h4>1. المقدمة</h4>'
                '<p>باستخدامك لموقع Furni فإنك توافق على الالتزام بالشروط والأحكام التالية. '
                'يرجى قراءتها بعناية قبل إتمام أي عملية شراء.</p>'
                '<h4>2. الطلبات والدفع</h4>'
                '<p>يتم تأكيد الطلب بعد استكمال بيانات الفوترة والشحن بشكل صحيح. '
                'الأسعار المعروضة تشمل جميع الضرائب المطبقة ما لم يُذكر خلاف ذلك.</p>'
                '<h4>3. الشحن والتوصيل</h4>'
                '<p>نسعى لتوصيل الطلبات خلال المدة المحددة، وقد تختلف المدة حسب الموقع الجغرافي والظروف الخارجة عن إرادتنا.</p>'
                '<h4>4. الإرجاع والاستبدال</h4>'
                '<p>يحق للعميل إرجاع المنتج خلال 14 يوماً من تاريخ الاستلام، بشرط أن يكون بحالته الأصلية وغير مستخدم.</p>'
                '<h4>5. الملكية الفكرية</h4>'
                '<p>جميع المحتويات الموجودة على الموقع (نصوص، صور، تصاميم) هي ملك حصري لـ Furni ولا يجوز استخدامها دون إذن مسبق.</p>'
            ),
        })
        LegalPage.objects.get_or_create(page_type='privacy', defaults={
            'title': 'Privacy Policy',
            'content': (
                '<h4>1. المعلومات التي نجمعها</h4>'
                '<p>نقوم بجمع المعلومات التي تقدمها مباشرة مثل الاسم، البريد الإلكتروني، رقم الهاتف، وعنوان الشحن '
                'عند إنشاء حساب أو إتمام عملية شراء.</p>'
                '<h4>2. كيفية استخدام المعلومات</h4>'
                '<p>نستخدم بياناتك لمعالجة الطلبات، تحسين تجربة التسوق، والتواصل معك بخصوص طلباتك وعروضنا (إن وافقت على ذلك).</p>'
                '<h4>3. حماية البيانات</h4>'
                '<p>نتخذ إجراءات أمنية معقولة لحماية بياناتك من الوصول أو الاستخدام أو الإفصاح غير المصرح به.</p>'
                '<h4>4. مشاركة البيانات</h4>'
                '<p>لا نشارك بياناتك الشخصية مع أطراف ثالثة إلا في حدود ما يلزم لإتمام عملية الشحن والدفع.</p>'
                '<h4>5. حقوقك</h4>'
                '<p>يمكنك في أي وقت طلب الاطلاع على بياناتك أو تعديلها أو حذفها من خلال التواصل معنا.</p>'
            ),
        })

        # --- Site settings ---
        SiteSetting.load()

        self.stdout.write(self.style.SUCCESS('✔ Seed data created successfully.'))
