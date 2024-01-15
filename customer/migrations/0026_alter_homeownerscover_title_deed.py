# Generated by Django 5.0 on 2024-01-11 10:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0025_alter_homeownerscover_title_deed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homeownerscover',
            name='title_deed',
            field=models.FileField(blank=True, max_length=255, null=True, upload_to='', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])]),
        ),
    ]
