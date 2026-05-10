from rest_framework import serializers

from audit_logs.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'order', 'order_number', 'old_status', 'new_status', 'changed_at']
