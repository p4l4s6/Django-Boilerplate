from django.urls import path, include

app_name = 'api-v1'

urlpatterns = [
    path('auth/', include('coreapp.api.urls')),
]
