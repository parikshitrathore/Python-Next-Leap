from rest_framework import viewsets
from warehouses.models import Warehouse
from .serializers import WarehouseSerializer
from base.permissions import IsAuthenticatedOrReadOnly

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
