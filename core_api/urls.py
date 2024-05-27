from django.urls import path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from core_api.views.scheme.scheme_list import SchemeListView

schema_view = get_schema_view(
    openapi.Info(
        title='core-api',
        default_version='v1',
    ),
    public=True,
)

urlpatterns = [
    path('scheme/', SchemeListView.as_view()),
]
