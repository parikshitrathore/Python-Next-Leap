from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from products.models import Product
from .serializers import ProductSerializer
from base.permissions import IsAuthenticatedOrReadOnly

from base.utils import LargeResultsSetPagination
# from django.utils.decorators import method_decorator
# from django.views.decorators.cache import cache_page

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'sku']
    ordering_fields = ['price', 'created_at']
    pagination_class = LargeResultsSetPagination  # required for pagination

    # @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)

    # CREATE
    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Product created successfully",
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
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                "message": "Products fetched successfully",
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
                "message": "Product fetched successfully",
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
                "message": "Product updated successfully",
                "data": serializer.data
            }
        )

    # DELETE
    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        delete_id = instance.id
        instance.delete()

        return Response(
            {
                "message": "Product deleted successfully",
                "data": {
                    "id": delete_id,
                    "sku": instance.sku,
                    "name": instance.name,
                    "description": instance.description,
                    "price": instance.price,
                    "is_active": instance.is_active,
                    "created_at": instance.created_at,
                    "updated_at": instance.updated_at,
                    "weight": instance.weight,
                }
            },
            status=status.HTTP_204_NO_CONTENT
        )