from django.urls import path, include

app_name = 'products'

urlpatterns = [
    path('v1/', include('products.api.v1.urls')),
]
