from functools import lru_cache

from django import forms
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import User, Access, SchemeMap


class RefreshEquipmentMapService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ["access_presence", "map_presence"]

    @lru_cache
    @property
    def _map(self) -> SchemeMap | None:
        try:
            return SchemeMap.objects.get(id=self.cleaned_data["id"])
        except SchemeMap.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        try:
            return Access.objects.get(user=self.cleaned_data['current_user'], scheme=self._map.scheme,
                                      role__in=['Change', 'Creator'])
        except Access.DoesNotExist:
            return None

    def access_presence(self) -> None:
        if self._map:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schem id = '
                                                                f'{self._map.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
