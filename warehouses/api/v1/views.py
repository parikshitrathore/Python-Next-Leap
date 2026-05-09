from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from warehouses.models import Warehouse
from .serializers import WarehouseSerializer


class WarehousePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class WarehouseFilter(filters.FilterSet):
    is_active = filters.BooleanFilter()

    class Meta:
        model = Warehouse
        fields = ['is_active']


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all().order_by('-created_at')
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = WarehousePagination
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = WarehouseFilter
    search_fields = ['name', 'city', 'state']
    ordering_fields = ['name', 'city', 'capacity', 'created_at']
    ordering = ['-created_at']
