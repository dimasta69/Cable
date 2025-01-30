from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status
from functools import lru_cache

from utils.fields import ModelField
from utils.services import ServiceWithResult
from django import forms

from models_app.models import Manufacturer, User


class ManufacturerDeleteService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['manufacturer_presence', 'is_superuser']

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

    def manufacturer_presence(self):
        if not self._manufacturer:
            self.add_error('id', ObjectDoesNotExist(f'Port template id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied(
                    "User is not superuser"
                )
            )
