from django.urls import path

from core_api.views.port.connection import ConnectionView

urlpatterns = [
    path("", ConnectionView.as_view()),
]
