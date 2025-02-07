# Generated by Django 5.1.3 on 2025-02-07 01:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_id', models.CharField(max_length=37)),
                ('balances_available', models.IntegerField()),
                ('balances_current', models.IntegerField()),
                ('balances_limit', models.IntegerField()),
                ('balances_iso_currency_code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=255)),
                ('official_name', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=25)),
                ('subtype', models.CharField(max_length=50)),
                ('linked_bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bank_accounts', to='core.linkedbank')),
            ],
        ),
    ]
