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

from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter

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
        # Problem: two users bought the same last item. > Solution: select_for_update > Lock this product row until this transaction finishes.
        if not inventory:
            continue
        # If inventory not found, skip that item.

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
    # controls allowed movement
    Order.Status.PENDING: [Order.Status.CONFIRMED, Order.Status.CANCELLED],
    Order.Status.CONFIRMED: [Order.Status.COMPLETED],
    Order.Status.CANCELLED: [],
    Order.Status.COMPLETED: [],
}

class OrderFilter(filters.FilterSet):
    status = filters.CharFilter()

    class Meta:
        model = Order
        fields = ['status']

class OrderViewSet(viewsets.GenericViewSet):
    # for custom logic
    serializer_class = OrderSerializer
    filter_backends = [
        filters.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = OrderFilter

    def get_permissions(self):
        # Only admin can update order status; all authenticated users can list/create/retrieve
        if self.action == 'update_status':
            return [IsAdminUser()]
        # Only admin can update order status.
        return [IsAuthenticated()]
    # All other order APIs require login.

    def get_queryset(self):
        # This decides which orders the current user can see
        user = self.request.user
        qs = Order.objects.prefetch_related('items__product')
        # Admin sees all orders; regular users see only their own
        if user.is_staff:
            return qs.all()
        return qs.filter(user=user)

    def list(self, request):
        # GET /orders/
        queryset = self.filter_queryset(self.get_queryset())
        # filter_queryset= Apply all DRF filters on this queryset
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        # GET /orders/{id}/
        # pk = primary key/id from URL
        order = self.get_queryset().filter(pk=pk).first()
        # .first()=Give me the first object from this queryset, or None if nothing is found
        if not order:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrderSerializer(order).data)

    def create(self, request):
        # POST /orders/
        input_serializer = CreateOrderSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        items_data = input_serializer.validated_data['items']

        try:
            with transaction.atomic():
                # Everything inside must succeed together.
                total_price = 0
                order_items_to_create = []

                for item_data in items_data:
                    # Loop each requested item
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
                    # bulk_create(): create many rows in database together.
                    OrderItem(order=order, **item)
                    # order=order links every item to the same order.  **item spreads the dictionary.
                    for item in order_items_to_create
                    # above code: Python list comprehension >  same as: order_items = []
                    # for item in order_items_to_create:
                    # order_item = OrderItem(order=order, **item)
                    # order_items.append(order_item)
                ])

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='status')
    # a custom PATCH API to update status of one specific order.
    # @action > used in DRF ViewSet when you want to create an extra API endpoint apart from normal CRUD APIs.
    # detail=True > API is for one specific record, so URL needs an id.
    def update_status(self, request, pk=None):
        # Admin can update any order, not scoped to their own
        # select_related('user') prevents an extra query when the post_save signal
        # on AuditLog accesses instance.order.user to create the notification.
        order = Order.objects.select_related('user').filter(pk=pk).first()
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
            # Save old status for audit log
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
            # Create status history record.

        return Response(OrderSerializer(order).data)
