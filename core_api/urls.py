from django.urls import path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from core_api.views.scheme.scheme_list import SchemeListView
from core_api.views.scheme.scheme import SchemeView

schema_view = get_schema_view(
    openapi.Info(
        title='core-api',
        default_version='v1',
    ),
    public=True,
)

urlpatterns = [
    path('scheme/', SchemeListView.as_view()),
    path('scheme/<int:id>/', SchemeView.as_view()),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
