from django.db import models
from accounts.models import Manager
from django.utils.text import slugify
import uuid

class Form(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
        ('trash', 'Trash')
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(Manager, on_delete=models.CASCADE, null=True)  # Allow null for superuser
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_template = models.BooleanField(default=False)
    form_data = models.JSONField(default=dict)  # Store form structure
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title + "-" + str(uuid.uuid4())[:8])
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f"/form/{self.slug}"
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
