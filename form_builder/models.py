from django.db import models
from django.utils.text import slugify
from django.conf import settings
import uuid
import json
import os
from django.contrib.auth import get_user_model

User = get_user_model()

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
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='form_submissions')
    responses = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def get_responses(self):
        return json.loads(self.responses)

    def __str__(self):
        return f"Submission for {self.form.title} at {self.created_at}"


def get_file_upload_path(instance, filename):
    # Generate a unique path for the uploaded file
    # Format: uploads/form_<form_id>/submission_<submission_id>/<filename>
    return os.path.join(
        'uploads',
        f'form_{instance.form_submission.form.id}',
        f'submission_{instance.form_submission.id}',
        filename
    )


class FileUpload(models.Model):
    form_submission = models.ForeignKey(FormSubmission, on_delete=models.CASCADE, related_name='file_uploads')
    field_label = models.CharField(max_length=255)  # The label of the form field
    file = models.FileField(upload_to=get_file_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.field_label} in {self.form_submission}"

    def filename(self):
        return os.path.basename(self.file.name)
