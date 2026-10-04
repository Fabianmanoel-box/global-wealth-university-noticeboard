from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=20, default='blue',
        help_text='Tailwind color: blue, green, red, yellow, purple, indigo'
    )

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('dashboard') + f'?category={self.slug}'


class Notice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='notices'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notices'
    )
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    is_important = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')
    published_at = models.DateTimeField(default=timezone.now)
    scheduled_at = models.DateTimeField(
        null=True, blank=True,
        help_text='If set in future, notice stays hidden until this date/time.'
    )
    expiry_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_important', '-published_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('notice_detail', args=[self.pk])

    @property
    def is_expired(self):
        if self.expiry_date and timezone.now() > self.expiry_date:
            return True
        return False

    @property
    def is_scheduled(self):
        if self.scheduled_at and timezone.now() < self.scheduled_at:
            return True
        return False

    @property
    def is_active(self):
        return self.status == 'published' and not self.is_expired and not self.is_scheduled

    def save(self, *args, **kwargs):
        # Auto-flip status based on scheduled_at
        if self.scheduled_at and self.scheduled_at > timezone.now():
            self.status = 'scheduled'
        elif self.status == 'scheduled' and (
            not self.scheduled_at or self.scheduled_at <= timezone.now()
        ):
            self.status = 'published'
        super().save(*args, **kwargs)

    def auto_publish_if_due(self):
        """If scheduled time has passed, flip to published."""
        if (
            self.status == 'scheduled'
            and self.scheduled_at
            and self.scheduled_at <= timezone.now()
        ):
            self.status = 'published'
            self.save(update_fields=['status'])