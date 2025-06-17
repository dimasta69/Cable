from django.urls import path

from core_api.views.type_port.list import TypePortListView

urlpatterns = [
    path('', TypePortListView.as_view()),

]
