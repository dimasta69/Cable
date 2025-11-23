from django.urls import path

from license_api.views.mac.mac import MacView

urlpatterns = [
    path('', MacView.as_view()),
]
