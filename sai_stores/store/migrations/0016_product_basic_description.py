# Generated by Django 5.1.5 on 2025-02-05 16:44

import tinymce.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_alter_product_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='basic_description',
            field=tinymce.models.HTMLField(default=1),
            preserve_default=False,
        ),
    ]
