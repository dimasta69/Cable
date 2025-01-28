from django.urls import path

from core_api.views.room.room import RoomView
from core_api.views.room.list import RoomListView

urlpatterns = [
    path('', RoomListView.as_view()),
    path('<int:id>/', RoomView.as_view()),
]
