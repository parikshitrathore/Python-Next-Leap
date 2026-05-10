import uuid

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from audit_logs.models import AuditLog
from inventory.models import Inventory
from orders.models import Order, OrderItem
from products.models import Product
from .serializers import CreateOrderSerializer, OrderSerializer, OrderStatusUpdateSerializer

def _update_inventory_on_status_change(order, new_status):
    """
    COMPLETED → actually deduct stock (reserved → consumed)
    CANCELLED  → release the reservation (reserved → free again)
    CONFIRMED  → no inventory change (stock stays reserved)
    """
    if new_status not in (Order.Status.COMPLETED, Order.Status.CANCELLED):
        return

    items = order.items.select_related('product').all()
    for item in items:
        inventory = (
            Inventory.objects
            .select_for_update()
            .filter(product=item.product)
            .first()
        )
        if not inventory:
            continue

        if new_status == Order.Status.COMPLETED:
            # Stock is physically consumed — deduct from both fields
            inventory.quantity_available -= item.quantity
            inventory.reserved_quantity -= item.quantity
        elif new_status == Order.Status.CANCELLED:
            # Release the hold — quantity_available stays the same
            inventory.reserved_quantity -= item.quantity

        inventory.save()


# Allowed status transitions
VALID_TRANSITIONS = {
    Order.Status.PENDING: [Order.Status.CONFIRMED, Order.Status.CANCELLED],
    Order.Status.CONFIRMED: [Order.Status.COMPLETED],
    Order.Status.CANCELLED: [],
    Order.Status.COMPLETED: [],
}


class OrderViewSet(viewsets.GenericViewSet):
    serializer_class = OrderSerializer

    def get_permissions(self):
        # Only admin can update order status; all authenticated users can list/create/retrieve
        if self.action == 'update_status':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.prefetch_related('items__product')
        # Admin sees all orders; regular users see only their own
        if user.is_staff:
            return qs.all()
        return qs.filter(user=user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        order = self.get_queryset().filter(pk=pk).first()
        if not order:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrderSerializer(order).data)

    def create(self, request):
        input_serializer = CreateOrderSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        items_data = input_serializer.validated_data['items']

        try:
            with transaction.atomic():
                total_price = 0
                order_items_to_create = []

                for item_data in items_data:
                    product_id = item_data['product_id']
                    quantity = item_data['quantity']

                    # Validate product exists and is active
                    try:
                        product = Product.objects.get(id=product_id)
                    except Product.DoesNotExist:
                        raise ValueError(f"Product with id {product_id} does not exist.")

                    if not product.is_active:
                        raise ValueError(f"Product '{product.name}' is not active.")

                    # Lock inventory row to prevent race conditions
                    inventory = (
                        Inventory.objects
                        .select_for_update()
                        .filter(product=product)
                        .first()
                    )

                    if not inventory:
                        raise ValueError(f"No inventory found for product '{product.name}'.")

                    available_stock = inventory.quantity_available - inventory.reserved_quantity
                    if available_stock < quantity:
                        raise ValueError(
                            f"Insufficient stock for '{product.name}'. "
                            f"Available: {available_stock}, Requested: {quantity}."
                        )

                    # Reserve the stock — don't deduct yet, order is still pending
                    inventory.reserved_quantity += quantity
                    inventory.save()

                    total_price += product.price * quantity
                    order_items_to_create.append({
                        'product': product,
                        'quantity': quantity,
                        'price_at_purchase': product.price,
                    })

                order = Order.objects.create(
                    user=request.user,
                    order_number=f"ORD-{uuid.uuid4().hex[:8].upper()}",
                    status=Order.Status.PENDING,
                    total_price=total_price,
                )

                OrderItem.objects.bulk_create([
                    OrderItem(order=order, **item)
                    for item in order_items_to_create
                ])

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        # Admin can update any order, not scoped to their own
        order = Order.objects.filter(pk=pk).first()
        if not order:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_status = serializer.validated_data['status']
        allowed = VALID_TRANSITIONS.get(order.status, [])

        if new_status not in allowed:
            return Response(
                {'error': f"Cannot transition from '{order.status}' to '{new_status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        old_status = order.status
        with transaction.atomic():
            order.status = new_status
            order.save()

            # Update inventory based on status transition
            _update_inventory_on_status_change(order, new_status)

            AuditLog.objects.create(
                order=order,
                old_status=old_status,
                new_status=new_status,
            )

        return Response(OrderSerializer(order).data)
