# Generated by Django 3.0.5 on 2023-12-05 09:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0007_customer_id_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThirdPartyCarInsurance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_date', models.DateField(auto_now_add=True)),
                ('file_upload', models.FileField(blank=True, null=True, upload_to='Forms/ThirdPartyCarInsurance/')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='car_insurance_covers', to='customer.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='KYCForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_date', models.DateField(auto_now_add=True)),
                ('file_upload', models.FileField(blank=True, null=True, upload_to='Forms/KYC/')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kyc_forms', to='customer.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='HomeownersCover',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_date', models.DateField(auto_now_add=True)),
                ('file_upload', models.FileField(blank=True, null=True, upload_to='Forms/HomeOwnersCover/')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='homeowners_covers', to='customer.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='DirectDebitForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_date', models.DateField(auto_now_add=True)),
                ('file_upload', models.FileField(blank=True, null=True, upload_to='Forms/DirectDebit/')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='direct_debit_forms', to='customer.Customer')),
            ],
        ),
    ]