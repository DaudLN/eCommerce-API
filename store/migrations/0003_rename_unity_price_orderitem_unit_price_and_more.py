# Generated by Django 4.1.4 on 2023-04-26 22:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_product_slug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitem',
            old_name='unity_price',
            new_name='unit_price',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='price',
            new_name='unit_price',
        ),
    ]
