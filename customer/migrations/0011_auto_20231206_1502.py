# Generated by Django 3.0.5 on 2023-12-06 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0010_auto_20231206_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homeownerscover',
            name='customer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='homeowners_cover', to='customer.Customer'),
        ),
    ]
