# Generated by Django 3.2.8 on 2021-10-20 04:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_alter_product_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='times_purchased',
            field=models.IntegerField(default=0),
        ),
    ]
