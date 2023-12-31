# Generated by Django 3.0.5 on 2023-11-21 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0003_auto_20231115_1419'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='alternate_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='id_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='occupation',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='physical_address',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='postal_address',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
