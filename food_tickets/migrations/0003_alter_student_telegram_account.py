# Generated by Django 3.2.9 on 2022-10-16 21:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20221016_2020'),
        ('food_tickets', '0002_auto_20221017_0025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='telegram_account',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.telegramuser'),
        ),
    ]
