from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint


class Inventory(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='inventories')
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.CASCADE, related_name='inventories')
    quantity_available = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            # this pair must be unique: product + warehouse
            UniqueConstraint(fields=['product', 'warehouse'], name='unique_product_warehouse'),
        ]
        indexes = [
            # Searching/filtering
            models.Index(fields=['product', 'warehouse']),
            # show me all iphones from this warehouse
            models.Index(fields=['warehouse']),
            # show me all the product inventories in this warehouse
        ]

    def clean(self):
        if self.reserved_quantity > self.quantity_available:
            raise ValidationError(
                {'reserved_quantity': 'Reserved quantity cannot exceed quantity available.'}
            )

    def __str__(self):
        return f"{self.product} @ {self.warehouse}"
