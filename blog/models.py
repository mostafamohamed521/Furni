from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify


class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name_plural = 'Blog Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Post(models.Model):
    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='posts')
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    excerpt = models.CharField(max_length=300, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blog/')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            n = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f'{base_slug}-{n}'
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    @property
    def comment_count(self):
        return self.comments.filter(is_approved=True).count()


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    body = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
