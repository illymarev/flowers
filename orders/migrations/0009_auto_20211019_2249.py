# Generated by Django 3.2.8 on 2021-10-20 02:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_auto_20211019_2249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='order',
            name='tax',
            field=models.FloatField(),
        ),
    ]