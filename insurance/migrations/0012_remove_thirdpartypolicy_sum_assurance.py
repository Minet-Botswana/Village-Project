# Generated by Django 5.0 on 2024-02-19 09:37

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("insurance", "0011_alter_policy_premium_alter_policy_sum_assurance_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="thirdpartypolicy",
            name="sum_assurance",
        ),
    ]
