from django import forms
from functools import lru_cache

from typing import List

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import EquipmentScheme, SchemeMap, Access, User, Scheme


class EquipmentListService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)
    map_content_type = ContentType.objects.get_for_model(SchemeMap)

    custom_validations = ['map_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._equipment_list
        return self

    @property
    def _equipment_list(self) -> List[EquipmentScheme]:
        try:
            return EquipmentScheme.objects.filter(schemes=self._map)
        except EquipmentScheme.DoesNotExist:
            return EquipmentScheme.objects.none()

    @property
    @lru_cache()
    def _map(self) -> SchemeMap | None:
        try:
            return SchemeMap.objects.get(id=self.cleaned_data['id'])
        except SchemeMap.DoesNotExist:
            return None

    @property
    def _access(self):
        try:
            return Access.objects.filter(
                Q(
                    object_type=self.scheme_content_type,
                    object_id=self._map.scheme.pk,
                ),
            ).filter(
                user=self.cleaned_data['current_user'],
            )
        except Access.DoesNotExist:
            return None

    def map_presence(self) -> None:
        if not self._map:
            self.add_error(
                "id",
                NotFound(
                    f"Map id={self.cleaned_data['id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if self.cleaned_data['id']:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the map id = '
                                                                f'{self.cleaned_data["id"]} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
