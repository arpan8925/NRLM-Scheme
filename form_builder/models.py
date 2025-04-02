from django.db import models
from django.utils.text import slugify
from django.conf import settings
import uuid
import json

class Form(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    fields = models.TextField(default='[]')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/form/{self.slug}"

    class Meta:
        ordering = ['-created_at']

class FormSubmission(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='submissions')
    responses = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def get_responses(self):
        return json.loads(self.responses)

    def __str__(self):
        return f"Submission for {self.form.title} at {self.created_at}"
