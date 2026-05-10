import hashlib

from django.core.cache import cache
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from base.permissions import IsAdminUserOrReadOnly
from products.models import Product
from .serializers import ProductSerializer

PRODUCT_CACHE_TTL = 120  # 2 minutes


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductFilter(filters.FilterSet):
    is_active = filters.BooleanFilter()

    class Meta:
        model = Product
        fields = ['is_active']


class ProductViewSet(viewsets.ModelViewSet):
    # queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    # Read (list/retrieve) → anyone; Write (create/update/delete) → admin only
    permission_classes = [IsAdminUserOrReadOnly]
    pagination_class = ProductPagination
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filter_backends > think of as features enabled on list API.
    filterset_class = ProductFilter
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Product.objects.all()

        # By default show only active products
        is_active = self.request.query_params.get('is_active')

        if is_active is None:
            queryset = queryset.filter(is_active=True)

        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        # overriding default list 
        # Each unique combination of query params gets its own cache key
        query_string = request.GET.urlencode()
        # gets query params from URL, Because every different query should have different cache.
        cache_key = f"product_list_{hashlib.md5(query_string.encode()).hexdigest()}"
        # creates a short unique cache key.

        cached_data = cache.get(cache_key)
        # Do we already have response for this exact query?
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        # If cache does not exist, call DRF’s original list method.
        cache.set(cache_key, response.data, PRODUCT_CACHE_TTL)
        # Stores response in cache for 120 seconds. > cache expires after 2 minutes
        return response

    def _invalidate_product_cache(self):
        cache.delete_pattern('product_list_*')
        # deletes all cached product list results.

    def perform_create(self, serializer):
        serializer.save()
        self._invalidate_product_cache()

    def perform_update(self, serializer):
        serializer.save()
        self._invalidate_product_cache()
        # When product is updated, cached list may be wrong.So clear cache

    def perform_destroy(self, instance):
        instance.delete()
        self._invalidate_product_cache()
        # When product is deleted, cached list may still show deleted product. So clear cache.
