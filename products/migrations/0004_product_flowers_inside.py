# Generated by Django 3.2.8 on 2021-10-06 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_singleflower'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='flowers_inside',
            field=models.ManyToManyField(to='products.SingleFlower'),
        ),
    ]
