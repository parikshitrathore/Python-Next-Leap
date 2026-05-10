from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('warehouses/', include('warehouses.urls')),
    path('inventory/', include('inventory.urls')),
]