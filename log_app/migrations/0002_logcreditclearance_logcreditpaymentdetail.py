# Generated by Django 3.1.9 on 2021-07-15 10:53

from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('sale', '0001_initial'),
        ('credit_management', '0001_initial'),
        ('core_app', '0001_initial'),
        ('log_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogCreditPaymentDetail',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('history_date_bs', models.CharField(blank=True, max_length=10, null=True)),
                ('amount', models.DecimalField(decimal_places=2, help_text='max_value upto 9999999999.99', max_digits=12)),
                ('remarks', models.CharField(blank=True, help_text='Remarks can have max of 50 characters, blank=True', max_length=50)),
                ('history_user_id', models.IntegerField(null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('credit_clearance', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='credit_management.creditclearance')),
                ('payment_mode', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core_app.paymentmode')),
            ],
            options={
                'verbose_name': 'historical credit payment detail',
                'db_table': 'credit_management_creditpaymentdetail_log',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='LogCreditClearance',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('history_date_bs', models.CharField(blank=True, max_length=10, null=True)),
                ('payment_type', models.PositiveIntegerField(choices=[(1, 'PAYMENT'), (2, 'REFUND')], default=1, help_text='Where 1 = PAYMENT, 2 = REFUND, default=1')),
                ('receipt_no', models.CharField(help_text='receipt_no can be upto 20 characters', max_length=20)),
                ('total_amount', models.DecimalField(decimal_places=2, help_text='max_value upto 9999999999.99, min_value=0.0', max_digits=12)),
                ('remarks', models.CharField(blank=True, help_text='Remarks can have max of 50 characters, blank=True', max_length=50)),
                ('history_user_id', models.IntegerField(null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('ref_credit_clearance', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='credit_management.creditclearance')),
                ('sale_main', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sale.salemain')),
            ],
            options={
                'verbose_name': 'historical credit clearance',
                'db_table': 'credit_management_creditclearance_log',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
