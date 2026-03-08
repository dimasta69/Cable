from django.core.exceptions import PermissionDenied
from rest_framework import status
from functools import lru_cache

from core_api.utils.presence import PresenceChecksMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from django import forms

from models_app.models import Manufacturer, User


class ManufacturerDeleteService(PresenceChecksMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['run_presence_checks', 'is_superuser']
    presence_checks = [("_manufacturer", "id", "Manufacturer")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._delete_manufacturer()
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    def _delete_manufacturer(self) -> None:
        self._manufacturer.delete()

    @property
    @lru_cache()
    def _manufacturer(self) -> Manufacturer | None:
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['id'])
        except Manufacturer.DoesNotExist:
            return None

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied(
                    "User is not superuser"
                )
            )
