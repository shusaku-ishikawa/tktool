# Generated by Django 3.0.7 on 2020-07-22 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20200721_0016'),
    ]

    operations = [
        migrations.AddField(
            model_name='appsettings',
            name='use_paypal',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
