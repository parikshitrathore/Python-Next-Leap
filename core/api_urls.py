from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    # Add other API urls here, for example:
    # path('base/', include('base.urls')),
]