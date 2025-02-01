from django import forms
from functools import lru_cache

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework import status

from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import EquipmentScheme, User, Access, Scheme, SchemeMap


class UpdateEquipmentService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    coord_x = forms.IntegerField(required=False)
    coord_y = forms.IntegerField(required=False)
    current_user = ModelField(User)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)
    map_content_type = ContentType.objects.get_for_model(SchemeMap)

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
            return EquipmentScheme.objects.select_related('schemes__scheme', 'schemes').get(id=self.cleaned_data['id'])
        except EquipmentScheme.DoesNotExist:
            return None

    @property
    def _access(self):
        try:
            return Access.objects.filter(
                Q(
                    object_type=self.map_content_type,
                    object_id=self._equipment.schemes.pk,
                )|
                Q(
                    object_type=self.scheme_content_type,
                    object_id=self._equipment.schemes.scheme.pk,
                ),
            ).filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator']
            )
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
