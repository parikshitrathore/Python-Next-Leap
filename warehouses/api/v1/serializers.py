from rest_framework import serializers

from warehouses.models import Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'city', 'state', 'capacity', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
