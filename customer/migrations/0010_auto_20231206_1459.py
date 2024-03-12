# Generated by Django 3.0.5 on 2023-12-06 14:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customer', '0009_auto_20231205_0927'),
    ]

    operations = [
        migrations.RenameField(
            model_name='homeownerscover',
            old_name='file_upload',
            new_name='title_deed',
        ),
        migrations.AddField(
            model_name='homeownerscover',
            name='district',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='homeownerscover',
            name='financial_interest',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='homeownerscover',
            name='geo_location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='homeownerscover',
            name='plot_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='homeownerscover',
            name='village',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='homeownerscover',
            name='ward',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='homeownerscover',
            name='customer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='homeowners_cover', to=settings.AUTH_USER_MODEL),
        ),
    ]
