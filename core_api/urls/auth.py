from django.urls import path

from core_api.views.auth.login import TokenCreateView
from core_api.views.auth.logout import TokenDestroyView

urlpatterns = [
    path('token/login/', TokenCreateView.as_view()),
    path('token/logout/', TokenDestroyView.as_view()),
]
