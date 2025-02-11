from .models import Order, OrderItem
from rest_framework import serializers



class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
        extra_kwargs = {'seller': {'write_only': True}}


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['order_number']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        seller = validated_data['seller']
        last_order = Order.objects.filter(seller=seller).order_by('-order_number').first()
        order_number = last_order.order_number + 1 if last_order else 1
        items = []
        for item_data in items_data:
            order_item = OrderItem.objects.create(**item_data)
            items.append(order_item.id)

        order = Order.objects.create(order_number=order_number, **validated_data)
        for item in items:
            order.items.add(item)

        order.total_price = sum(item.food_item.price * item.quantity for item in order.items.all())
        if order.payment_method == "UPI":
            order.generate_qr_code_url()

        if order.payment_method == "CASH":
            order.order_status = 'PAID'

        order.save()
        return order


class OrderViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'order_id', 'order_number', 'total_price', 'payment_method', 'payment_code', 'order_status', 'created_at']
