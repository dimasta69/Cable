from django.urls import path

from core_api.views.users.users_list import UsersListView

urlpatterns = [
    path('', UsersListView.as_view()),
]
