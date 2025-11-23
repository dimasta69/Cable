from django.urls import path, include


urlpatterns = [
    path('mac/', include('license_api.urls.mac')),
    path('license_file/', include("license_api.urls.license")),
]
