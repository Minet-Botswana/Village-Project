# Generated by Django 5.0 on 2024-02-19 09:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("insurance", "0010_policy_expiry_date_thirdpartypolicy"),
    ]

    operations = [
        migrations.AlterField(
            model_name="policy",
            name="premium",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name="policy",
            name="sum_assurance",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name="thirdpartypolicy",
            name="premium",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name="thirdpartypolicy",
            name="sum_assurance",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
