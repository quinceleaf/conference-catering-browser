# Generated by Django 3.2 on 2021-04-18 22:45

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0005_alter_user_tenant'),
        ('orders', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderRepeat',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(default='DEFAULT', max_length=48)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AlterField(
            model_name='orderbase',
            name='date_approved',
            field=models.DateTimeField(blank=True, help_text='Date Approved', null=True, verbose_name='Approved'),
        ),
        migrations.AlterField(
            model_name='orderbase',
            name='date_submitted',
            field=models.DateTimeField(blank=True, help_text='Date Submitted', null=True, verbose_name='Submitted'),
        ),
        migrations.AlterField(
            model_name='orderlogistics',
            name='event_breakdown',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2010, 1, 1, 0, 0, tzinfo=utc), help_text='Breakdown', null=True),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment_methods', to='users.tenant'),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment_methods', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orderbase',
            name='repeat',
            field=models.ForeignKey(blank=True, help_text='Order Repeat', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='orders.orderrepeat'),
        ),
    ]