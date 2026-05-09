from rest_framework import serializers

from products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'description', 'price', 'weight', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
