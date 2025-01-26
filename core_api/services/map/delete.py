from django import forms
from functools import lru_cache

from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotFound

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import User, EquipmentScheme, Access


class DeleteEquipmentSchemeService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['access_presence', 'equipment_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._delete_equipment()
        return self

    def _delete_equipment(self) -> None:
        equipment = self._equipment
        equipment.delete()

    @property
    @lru_cache()
    def _equipment(self) -> EquipmentScheme | None:
        try:
            return EquipmentScheme.objects.get(id=self.cleaned_data['id'])
        except EquipmentScheme.DoesNotExsist:
            return None

    @property
    def _access(self) -> Access | None:
        try:
            return Access.objects.get(
                user=self.cleaned_data['current_user'],
                scheme=self._equipment.schemes.scheme if self._equipment else None,
                role__in=['Change', 'Creator'])
        except Access.DoesNotExist:
            return None

    def access_presence(self) -> None:
        if self.cleaned_data['id']:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the map id = '
                                                                f'{self.cleaned_data["id"]} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN

    def equipment_presence(self) -> None:
        if not self._equipment:
            self.add_error(
                "id",
                NotFound(
                    f"Equipment map with id={self.cleaned_data['id']} not fund"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND
