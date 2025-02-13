from django import forms
from django.db.models import Q
from functools import lru_cache
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework import status
from django.contrib.contenttypes.models import ContentType

from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import User, SchemeMap, Access, Scheme


class DeleteMapService(ServiceWithResult):
    id = forms.IntegerField(required=False)
    current_user = ModelField(User)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)

    custom_validations = ["map_presence", "access_presence",]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._delete_map()
        return self

    def _delete_map(self) -> None:
        self._map.delete()

    @property
    @lru_cache
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

    def map_presence(self) -> None:
        if self.cleaned_data['id'] and not self._map:
            self.add_error(
                "id",
                NotFound(
                    f"Map id={self.cleaned_data['id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND
