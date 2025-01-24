from django import forms
from functools import lru_cache

from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework import status

from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import EquipmentScheme, User, Access


class UpdateEquipmentService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    coord_x = forms.IntegerField(required=False)
    coord_y = forms.IntegerField(required=False)
    current_user = ModelField(User)

    custom_validations = ['equipment_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_equipment
        return self

    @property
    def _update_equipment(self) -> EquipmentScheme:
        equipment = self._equipment
        if self.cleaned_data['coord_x']:
            equipment.coord_x = self.cleaned_data['coord_x']
        if self.cleaned_data['coord_y']:
            equipment.coord_y = self.cleaned_data['coord_y']
        equipment.save()
        return equipment

    @property
    @lru_cache()
    def _equipment(self) -> EquipmentScheme | None:
        try:
            return EquipmentScheme.objects.select_related('schemes__scheme').get(id=self.cleaned_data['id'])
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

    def equipment_presence(self) -> None:
        if not self._equipment:
            self.add_error(
                "id",
                NotFound(
                    f"Equipment map with id={self.cleaned_data['id']} not fund"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if self.cleaned_data['id']:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user',
                               PermissionDenied(
                                   'Access to the scheme id = '
                                   f'{self._equipment.schemes.scheme.id if self._equipment else None} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
