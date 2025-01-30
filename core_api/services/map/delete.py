from django import forms
from functools import lru_cache

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotFound

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import User, EquipmentScheme, Access, Scheme, SchemeMap


class DeleteEquipmentSchemeService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)
    map_content_type = ContentType.objects.get_for_model(SchemeMap)

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
            return EquipmentScheme.objects.select_related("schemes", "schemes__scheme").get(id=self.cleaned_data['id'])
        except EquipmentScheme.DoesNotExsist:
            return None

    @property
    def _access(self):
        try:
            return Access.objects.filter(
                Q(
                    object_type=self.map_content_type,
                    object_id=self._equipment.schemes.id,
                ),
                Q(
                    object_type=self.scheme_content_type,
                    object_id=self._equipment.schemes.scheme.id,
                ),
            ).filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator']
            )
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
