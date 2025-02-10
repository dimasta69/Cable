from functools import lru_cache

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status

from models_app.models import Access, User, Building, Scheme
from utils.fields import ModelField
from utils.services import ServiceWithResult


class DeleteBuildingService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)

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

    @property
    @lru_cache()
    def _building(self) -> Building | None:
        try:
            return Building.objects.get(id=self.cleaned_data["id"])
        except Building.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        try:
            return Access.objects.get(
                user=self.cleaned_data["current_user"],
                object_id=self._building.scheme.id,
                role__in=["Change", "Creator"],
                object_type=self.scheme_content_type,
            )
        except Access.DoesNotExist:
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

    def access_presence(self) -> None:
        if self._building:
            if not self._access and not self.cleaned_data["current_user"].is_superuser:
                self.add_error(
                    "current_user",
                    PermissionDenied(
                        "Access to the schema id = "
                        f"{self._building.scheme.id} is not granted"
                    ),
                )
                self.response_status = status.HTTP_403_FORBIDDEN
