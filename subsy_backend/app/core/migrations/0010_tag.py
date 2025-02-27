# Generated by Django 5.1.3 on 2025-02-27 02:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_application_manage_subscription_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('subscriptions', models.ManyToManyField(related_name='tags', to='core.subscription')),
            ],
        ),
    ]
