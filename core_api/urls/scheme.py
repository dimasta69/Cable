from django.urls import path

from core_api.views.scheme.scheme import SchemeView
from core_api.views.scheme.list import SchemeListView
from core_api.views.figure.list import FigureListView
from core_api.views.figure.figure import UpdateFigureView

urlpatterns = [
    path('', SchemeListView.as_view()),
    path('<int:id>/', SchemeView.as_view()),
    path('figure/', FigureListView.as_view()),
    path('figure/<int:id>/', UpdateFigureView.as_view()),
]
