from django.db import models


class ContactMessage(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.created_at:%Y-%m-%d}'


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=150, blank=True)
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=150)
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    bio = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class Service(models.Model):
    title = models.CharField(max_length=150)
    icon_class = models.CharField(max_length=60, default='fa-solid fa-couch', help_text='Font Awesome icon class')
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class SiteSetting(models.Model):
    """Singleton-style model for global editable site info."""
    address = models.CharField(max_length=255, default='43 Raymouth Rd. Baltemoer, London 3910')
    email = models.EmailField(default='info@furni.com')
    phone = models.CharField(max_length=30, default='+1 294 3925 3939')
    facebook_url = models.URLField(blank=True, default='#')
    twitter_url = models.URLField(blank=True, default='#')
    instagram_url = models.URLField(blank=True, default='#')
    linkedin_url = models.URLField(blank=True, default='#')

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return 'Site Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['order']

    def __str__(self):
        return self.question


class LegalPage(models.Model):
    """Editable legal pages: Terms & Conditions, Privacy Policy."""
    PAGE_CHOICES = [
        ('terms', 'Terms & Conditions'),
        ('privacy', 'Privacy Policy'),
    ]
    page_type = models.CharField(max_length=20, choices=PAGE_CHOICES, unique=True)
    title = models.CharField(max_length=150)
    content = models.TextField(help_text='You can use basic HTML tags.')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
