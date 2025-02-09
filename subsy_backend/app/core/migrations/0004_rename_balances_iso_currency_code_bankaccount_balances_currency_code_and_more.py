# Generated by Django 5.1.3 on 2025-02-09 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_bankaccount_balances_available_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bankaccount',
            old_name='balances_iso_currency_code',
            new_name='balances_currency_code',
        ),
        migrations.AlterField(
            model_name='bankaccount',
            name='account_id',
            field=models.CharField(max_length=37, unique=True),
        ),
    ]
