# Generated by Django 5.1.6 on 2025-03-10 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LoanApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='otpverification',
            name='is_used',
            field=models.BooleanField(default=False),
        ),
    ]
