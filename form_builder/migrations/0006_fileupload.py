# Generated by Django 5.0.9 on 2025-04-11 19:18

import django.db.models.deletion
import form_builder.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form_builder', '0005_alter_formsubmission_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_label', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to=form_builder.models.get_file_upload_path)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('form_submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='file_uploads', to='form_builder.formsubmission')),
            ],
        ),
    ]
