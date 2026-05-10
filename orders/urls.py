from django.urls import path, include

app_name = 'orders'

urlpatterns = [
    path('v1/', include('orders.api.v1.urls')),
]
