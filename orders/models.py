from django.db import models
from django.conf import settings
from django.urls import reverse
import uuid


class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    discount_percent = models.PositiveIntegerField(help_text='Percentage e.g. 10 for 10%')
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_to = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.code} (-{self.discount_percent}%)'


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    country = models.CharField(max_length=80)
    company_name = models.CharField(max_length=120, blank=True)
    address = models.CharField(max_length=250)
    apartment = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    notes = models.TextField(blank=True)

    ship_to_different_address = models.BooleanField(default=False)
    shipping_address = models.CharField(max_length=250, blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_country = models.CharField(max_length=80, blank=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True)

    payment_method = models.CharField(max_length=30, default='cod', choices=[
        ('cod', 'Cash on Delivery'),
        ('bank_transfer', 'Direct Bank Transfer'),
        ('paypal', 'PayPal'),
    ])
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.order_number}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f'FRN-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('orders:order_detail', kwargs={'order_number': self.order_number})

    @property
    def items_subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def grand_total(self):
        return self.items_subtotal + self.shipping_cost - self.discount_amount

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('shop.Product', related_name='order_items', on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'

    @property
    def total_price(self):
        return self.price * self.quantity
