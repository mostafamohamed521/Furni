from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from shop.models import Product
from blog.models import Post


class ProductSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class BlogPostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Post.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return ['core:home', 'core:about', 'core:services', 'core:contact',
                'core:faq', 'shop:shop_list', 'blog:blog_list']

    def location(self, item):
        return reverse(item)
