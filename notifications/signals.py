from django.db.models.signals import post_save
from django.dispatch import receiver

from audit_logs.models import AuditLog
from notifications.models import Notification

STATUS_MESSAGES = {
    'confirmed': "Your order {order_number} has been confirmed.",
    'cancelled':  "Your order {order_number} has been cancelled.",
    'completed':  "Your order {order_number} has been completed.",
}


@receiver(post_save, sender=AuditLog)
def create_order_notification(sender, instance, created, **kwargs):
    if not created:
        return

    template = STATUS_MESSAGES.get(instance.new_status)
    if not template:
        return

    message = template.format(order_number=instance.order.order_number)
    Notification.objects.create(
        user=instance.order.user,
        message=message,
    )
