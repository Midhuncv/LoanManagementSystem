# Generated by Django 5.1.6 on 2025-03-16 09:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('user', 'User')], default='user', max_length=10)),
                ('email_verified', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='OTPVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp_code', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('is_used', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='otps', to='LoanApp.user')),
            ],
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_id', models.CharField(blank=True, max_length=20, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tenure', models.IntegerField(help_text='Loan tenure in  months')),
                ('interest_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('start_date', models.DateField(auto_now_add=True)),
                ('end_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('foreclosed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loans', to='LoanApp.user')),
            ],
        ),
    ]
