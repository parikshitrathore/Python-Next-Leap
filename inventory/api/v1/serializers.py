from rest_framework import serializers

from inventory.models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)

    class Meta:
        model = Inventory
        fields = [
            'id',
            'product', 'product_name',
            'warehouse', 'warehouse_name',
            'quantity_available',
            'reserved_quantity',
            'updated_at',
        ]

    def validate(self, data):
        quantity_available = data.get('quantity_available', getattr(self.instance, 'quantity_available', 0))
        reserved_quantity = data.get('reserved_quantity', getattr(self.instance, 'reserved_quantity', 0))
        if reserved_quantity > quantity_available:
            raise serializers.ValidationError(
                {'reserved_quantity': 'Reserved quantity cannot exceed quantity available.'}
            )
        return data
