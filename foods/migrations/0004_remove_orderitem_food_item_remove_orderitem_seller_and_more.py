# Generated by Django 4.2.19 on 2025-02-09 16:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0003_orderitem_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='food_item',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='seller',
        ),
        migrations.DeleteModel(
            name='Order',
        ),
        migrations.DeleteModel(
            name='OrderItem',
        ),
    ]
