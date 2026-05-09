from django.urls import path, include

app_name = 'warehouses'

urlpatterns = [
    path('v1/', include('warehouses.api.v1.urls')),
]
