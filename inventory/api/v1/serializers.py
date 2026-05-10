from rest_framework import serializers

from inventory.models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    # This is NOT model field. It is EXTRA field added only in API response. becasue product field will only give product id
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
        # data.get(new_value, old_value) =Use new request value if given, otherwise use existing DB value.
        # ex. use get only reserved_quantity in request, then quantity_available is missing. So it will fallback  to getattr(...)
        reserved_quantity = data.get('reserved_quantity', getattr(self.instance, 'reserved_quantity', 0))
        if reserved_quantity > quantity_available:
            raise serializers.ValidationError(
                {'reserved_quantity': 'Reserved quantity cannot exceed quantity available.'}
            )
        return data
