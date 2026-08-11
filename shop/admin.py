from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, Review, Wishlist


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('thumb', 'name', 'category', 'price', 'old_price', 'stock', 'is_active', 'is_featured', 'is_popular')
    list_editable = ('price', 'stock', 'is_active', 'is_featured', 'is_popular')
    list_filter = ('category', 'is_active', 'is_featured', 'is_popular')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    fieldsets = (
        ('Basic Info', {'fields': ('category', 'name', 'slug', 'sku')}),
        ('Description', {'fields': ('short_description', 'description', 'material', 'color')}),
        ('Pricing & Stock', {'fields': ('price', 'old_price', 'stock')}),
        ('Media', {'fields': ('image',)}),
        ('Flags', {'fields': ('is_active', 'is_featured', 'is_popular')}),
    )

    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:45px;height:45px;object-fit:cover;border-radius:6px;" />', obj.image.url)
        return '-'
    thumb.short_description = 'Image'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_approved', 'created_at')
    list_editable = ('is_approved',)
    list_filter = ('rating', 'is_approved')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
