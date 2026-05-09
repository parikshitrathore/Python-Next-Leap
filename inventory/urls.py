from django.urls import path, include

app_name = 'inventory'

urlpatterns = [
    path('v1/', include('inventory.api.v1.urls')),
]
