# Generated by Django 3.2.8 on 2021-10-31 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0013_order_bonus_points_used'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='actual_delivery',
            field=models.CharField(default='TBA', max_length=60),
        ),
    ]
