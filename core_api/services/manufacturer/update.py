from rest_framework import status
from django.core.exceptions import PermissionDenied

from core_api.utils.presence import PresenceChecksMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from django import forms
from functools import lru_cache

from models_app.models import Manufacturer, User


class ManufacturerUpdateService(PresenceChecksMixin, ServiceWithResult):
    name = forms.CharField(required=True)
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['run_presence_checks', 'name_presence', 'is_superuser']
    presence_checks = [("_manufacturer", "id", "Manufacturer")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_scheme()
            self.response_status = status.HTTP_200_OK
        return self

    def _update_scheme(self) -> Manufacturer:
        manufacturer = self._manufacturer
        manufacturer.name = self.cleaned_data['name']
        manufacturer.save()
        return manufacturer

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
