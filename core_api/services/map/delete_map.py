from django import forms
from functools import lru_cache
from rest_framework import status

from core_api.utils.access_checker import scope_for_map
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import User, SchemeMap


class DeleteMapService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=False)
    current_user = ModelField(User)

    custom_validations = ["run_presence_checks", "access_presence"]
    presence_checks = [("_map", "id", "Map", True)]  # only_if_set: id is optional

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
