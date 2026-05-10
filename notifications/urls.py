from django.urls import path, include

app_name = 'notifications'

urlpatterns = [
    path('v1/', include('notifications.api.v1.urls')),
]
