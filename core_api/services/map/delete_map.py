from django import forms
from functools import lru_cache
from rest_framework.exceptions import NotFound
from rest_framework import status

from core_api.utils.access_checker import scope_for_map
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import User, SchemeMap


class DeleteMapService(ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=False)
    current_user = ModelField(User)

    custom_validations = ["map_presence", "access_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._delete_map()
        return self

    def _delete_map(self) -> None:
        self._map.delete()

    def get_access_scope(self):
        return scope_for_map(self._map)

    @property
    @lru_cache()
    def _map(self) -> SchemeMap | None:
        try:
            return SchemeMap.objects.select_related('scheme').get(id=self.cleaned_data['id'])
        except SchemeMap.DoesNotExist:
            return None

    def map_presence(self) -> None:
        if self.cleaned_data.get('id') and not self._map:
            self.add_error(
                "id",
                NotFound(
                    f"Map id={self.cleaned_data['id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND
