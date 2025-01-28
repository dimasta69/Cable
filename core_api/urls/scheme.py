from django.urls import path

from core_api.views.scheme.scheme import SchemeView
from core_api.views.scheme.scheme_list import SchemeListView

urlpatterns = [
    path('', SchemeListView.as_view()),
    path('<int:id>/', SchemeView.as_view()),
]