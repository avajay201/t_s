# Generated by Django 4.2.19 on 2025-02-09 16:38

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('foods', '0004_remove_orderitem_food_item_remove_orderitem_seller_and_more'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('food_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foods.fooditem')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='accounts.seller')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('order_number', models.PositiveIntegerField()),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('payment_method', models.CharField(choices=[('CASH', 'Cash'), ('UPI', 'UPI')], default='CASH', max_length=10)),
                ('payment_status', models.CharField(choices=[('PENDING', 'Pending'), ('PAID', 'Paid'), ('CANCELLED', 'Cancelled'), ('FAILED', 'Failed')], default='PENDING', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('items', models.ManyToManyField(related_name='order', to='orders.orderitem')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='accounts.seller')),
            ],
            options={
                'unique_together': {('seller', 'order_number')},
            },
        ),
    ]
