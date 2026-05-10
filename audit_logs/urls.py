from django.urls import path, include

app_name = 'audit_logs'

urlpatterns = [
    path('v1/', include('audit_logs.api.v1.urls')),
]
