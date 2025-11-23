from django.urls import path

from license_api.views.license.license import LicenseView


urlpatterns = [
    path('', LicenseView.as_view()),
]
