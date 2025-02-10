# Generated by Django 4.2.19 on 2025-02-10 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_remove_orderitem_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='payment_status',
            new_name='order_status',
        ),
        migrations.AddField(
            model_name='order',
            name='payment_code',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='qr_expiry_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_id',
            field=models.CharField(editable=False, max_length=20, unique=True),
        ),
    ]
