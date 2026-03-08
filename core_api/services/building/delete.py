from functools import lru_cache

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from core_api.utils.access_checker import scope_for_building
from core_api.utils.scheme_access import ResourceAccessMixin
from models_app.models import User, Building
from utils.fields import ModelField
from utils.services import ServiceWithResult


class DeleteBuildingService(ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ["building_presence", "access_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._delete_building()
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    def _delete_building(self) -> None:
        self._building.delete()
        return None

    def get_access_scope(self):
        return scope_for_building(self._building)

    @property
    @lru_cache()
    def _building(self) -> Building | None:
        try:
            return Building.objects.get(id=self.cleaned_data["id"])
        except Building.DoesNotExist:
            return None

    def building_presence(self) -> None:
        if not self._building:
            self.add_error(
                "id",
                ObjectDoesNotExist(
                    "Building id=" f'{self.cleaned_data["id"]} not found'
                ),
            )
            self.response_status = status.HTTP_404_NOT_FOUND
