from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from inventory.models import Inventory
from .serializers import InventorySerializer


class InventoryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class InventoryFilter(filters.FilterSet):
    warehouse = filters.NumberFilter()
    product = filters.NumberFilter()

    class Meta:
        model = Inventory
        fields = ['warehouse', 'product']


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.select_related('product', 'warehouse').all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = InventoryPagination
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = InventoryFilter
    search_fields = ['product__name', 'warehouse__name']
    ordering_fields = ['quantity_available', 'reserved_quantity', 'updated_at']
    ordering = ['-updated_at']
