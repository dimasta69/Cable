from django import forms
from rest_framework.exceptions import NotFound
from rest_framework import status
from functools import lru_cache

from core_api.utils.access_checker import scope_for_scheme
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.services import ServiceWithResult
from core_api.utils.refresh_connection_building import refresh_connection_building
from models_app.models import Scheme, User
from utils.fields import ModelField


class RefreshBuildingConnectionService(ResourceAccessMixin, ServiceWithResult):
    scheme_id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ["access_presence", "scheme_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._refresh_connection_buildings()
        return self

    def _refresh_connection_buildings(self) -> None:
        refresh_connection_building(self._scheme)

    def get_access_scope(self):
        return scope_for_scheme(self._scheme)

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.prefetch_related("buildings").get(id=self.cleaned_data['scheme_id'])
        except Scheme.DoesNotExist:
            return None

    def scheme_presence(self) -> None:
        if not self._scheme:
            self.add_error(
                "scheme_id",
                NotFound(
                    f"Scheme id={self.cleaned_data['scheme_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND
