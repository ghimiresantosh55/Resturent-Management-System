# Generated by Django 3.1.9 on 2021-07-12 05:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import src.user.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(help_text='email should be unique with max length upto 150 characters', max_length=150, unique=True)),
                ('user_name', models.CharField(help_text='user_name must be unique and max_length upto 50 characters', max_length=50, unique=True)),
                ('first_name', models.CharField(blank=True, help_text='First name can have max_length upto 50 characters', max_length=50)),
                ('middle_name', models.CharField(blank=True, help_text='Middle name can have max_length upto 50 characters', max_length=50)),
                ('last_name', models.CharField(blank=True, help_text='Last name can have max_length upto 50 characters', max_length=50)),
                ('created_date_ad', models.DateTimeField(blank=True, null=True)),
                ('created_date_bs', models.CharField(blank=True, max_length=10, null=True)),
                ('is_staff', models.BooleanField(default=False, help_text='By default=True')),
                ('is_active', models.BooleanField(default=True)),
                ('gender', models.PositiveIntegerField(choices=[(1, 'Male'), (2, 'Female'), (3, 'Other')], default=1, help_text='where 1=male, 2=Female and 3=Other, default=1')),
                ('birth_date', models.DateField(blank=True, help_text='Blank=True and null=True', null=True)),
                ('address', models.TextField(blank=True, help_text='Address should be maximum of 50 characters', max_length=50)),
                ('mobile_no', models.CharField(blank=True, help_text='Mobile no. should be maximum of 15 characters', max_length=15)),
                ('photo', models.ImageField(blank=True, upload_to='user/', validators=[src.user.models.validate_image])),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
