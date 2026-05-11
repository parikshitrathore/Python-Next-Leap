from rest_framework import viewsets, filters, status, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from products.models import Product
from inventory.models import Inventory
from orders.models import Order, OrderItem
from .serializers import OrderCreateSerializer, OrderDetailSerializer, OrderStatusUpdateSerializer
from base.utils import LargeResultsSetPagination

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['order_number']
    ordering_fields = ['created_at', 'total_price']
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderStatusUpdateSerializer
        return OrderDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        items_data = serializer.validated_data['items']
        
        try:
            with transaction.atomic():
                order = Order.objects.create(user=request.user)
                total_price = 0

                for item in items_data:
                    product_id = item['product_id']
                    quantity = item['quantity']

                    # Validate product exists & is active
                    product = get_object_or_404(Product, id=product_id, is_active=True)
                    
                    #Validate stock exists & enough stock available [along with prevent race condition]
                    inventory_items = Inventory.objects.select_for_update().filter(
                        product=product, 
                        quantity_available__gte=quantity
                    )
                    if not inventory_items.exists():
                        raise ValidationError(
                            f"Insufficient stock for product: {product.name}"
                        )

                    inventory = inventory_items.first()

                    #Deduct inventory
                    inventory.quantity_available -= quantity
                    inventory.save()

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price_at_purchase=product.price
                    )
                    # Calculate total price
                    total_price += product.price * quantity

                order.total_price = total_price
                order.save()

                return Response({
                    "message": "Order created successfully",
                    "data": OrderDetailSerializer(order).data
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "message": "Orders fetched successfully",
            "count": queryset.count(),
            "data": serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "message": "Order fetched successfully",
            "data": serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Order updated successfully",
            "data": OrderDetailSerializer(instance).data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_id = instance.id
        instance.delete()

        return Response({
            "message": "Order deleted successfully",
            "data": {
                "id": delete_id,
                "order_number": instance.order_number
            }
        }, status=status.HTTP_204_NO_CONTENT)
