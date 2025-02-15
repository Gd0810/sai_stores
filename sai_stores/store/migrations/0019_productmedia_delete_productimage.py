# Generated by Django 5.1.5 on 2025-02-15 11:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0018_productimage_delete_productmedia'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='product_media/')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media_files', to='store.product')),
            ],
        ),
        migrations.DeleteModel(
            name='ProductImage',
        ),
    ]
