# Generated by Django 3.2.8 on 2021-10-20 02:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_order_wants_emails'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='tax',
            field=models.FloatField(default=0),
        ),
    ]
