# Generated by Django 5.0 on 2024-02-20 15:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer", "0027_alter_thirdpartycarinsurance_blue_book"),
        ("insurance", "0012_remove_thirdpartypolicy_sum_assurance"),
    ]

    operations = [
        migrations.CreateModel(
            name="ThirdpartyPolicyRecord",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("status", models.CharField(default="Pending", max_length=100)),
                ("creation_date", models.DateField(auto_now=True)),
                (
                    "Policy",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="insurance.policy",
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="customer.customer",
                    ),
                ),
            ],
        ),
    ]
