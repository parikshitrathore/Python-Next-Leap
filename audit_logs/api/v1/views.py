from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from audit_logs.models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListView(ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = AuditLog.objects.select_related('order').order_by('-changed_at')
        # Admin sees all audit logs; regular users see only their own orders' logs
        if user.is_staff:
            return qs
        return qs.filter(order__user=user)
