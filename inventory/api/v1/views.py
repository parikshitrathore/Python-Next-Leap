from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from inventory.models import Inventory

from .serializers import InventorySerializer
from base.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from base.utils import LargeResultsSetPagination

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    filterset_fields = [
        'product',
        'warehouse'
    ]

    search_fields = [
        'product__name',
        'warehouse__name'
    ]

    ordering_fields = [
        'quantity_available',
        'reserved_quantity',
        'updated_at'
    ]
    pagination_class = LargeResultsSetPagination

    # CREATE
    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Inventory created successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    # LIST
    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if page is not None:

            serializer = self.get_serializer(page, many=True)

            return self.get_paginated_response({
                "message": "Inventories fetched successfully",
                "count": len(serializer.data),
                "data": serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                "message": "Inventories fetched successfully",
                "count": queryset.count(),
                "data": serializer.data
            }
        )

    # RETRIEVE SINGLE
    def retrieve(self, request, *args, **kwargs):

        instance = self.get_object()

        serializer = self.get_serializer(instance)

        return Response(
            {
                "message": "Inventory fetched successfully",
                "data": serializer.data
            }
        )

    # UPDATE
    def update(self, request, *args, **kwargs):

        partial = kwargs.pop('partial', False)

        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Inventory updated successfully",
                "data": serializer.data
            }
        )

    # DELETE
    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()

        deleted_data = {
            "id": instance.id,
            "product": instance.product.name,
            "warehouse": instance.warehouse.name,
            "quantity_available": instance.quantity_available,
            "reserved_quantity": instance.reserved_quantity,
            "updated_at": instance.updated_at,
        }

        instance.delete()

        return Response(
            {
                "message": "Inventory deleted successfully",
                "data": deleted_data
            },
            status=status.HTTP_204_NO_CONTENT
        )