# Generated by Django 3.1.9 on 2021-07-27 10:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('log_app', '0002_logcreditclearance_logcreditpaymentdetail'),
    ]

    operations = [
        migrations.RenameField(
            model_name='logsalemain',
            old_name='is_real_time_upload',
            new_name='real_time_upload',
        ),
    ]
