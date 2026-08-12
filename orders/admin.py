from django.contrib import admin
from .models import Order, OrderItem, Coupon


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'email', 'phone', 'status', 'paid', 'grand_total_display', 'created_at')
    list_filter = ('status', 'paid', 'payment_method', 'created_at')
    search_fields = ('order_number', 'first_name', 'last_name', 'email', 'phone')
    list_editable = ('status', 'paid')
    inlines = [OrderItemInline]
    readonly_fields = ('order_number', 'created_at', 'updated_at')

    def grand_total_display(self, obj):
        return f'${obj.grand_total:.2f}'
    grand_total_display.short_description = 'Total'


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'active', 'valid_from', 'valid_to')
    list_editable = ('active',)
