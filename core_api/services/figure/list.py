from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework import status

from typing import List

from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Figure, User, Scheme, SchemeMap, Access


class FigureListService(ServiceWithResult):
    current_user = ModelField(User)
    filter_map_id = forms.IntegerField(required=True)

    custom_validations = ["access_presence", "map_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._figures
        return self

    @property
    def _figures(self) -> List[Figure]:
        try:
            return Figure.objects.filter(schemes=self._map)
        except Figure.DoesNotExist:
            return Figure.objects.none()

    @property
    def _map(self) -> SchemeMap | None:
        try:
            return SchemeMap.objects.get(id=self.cleaned_data['map_id'])
        except SchemeMap.DoesNotExist:
            return None

    @property
    def _access(self) -> List[Access] | None:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        map_content_type = ContentType.objects.get_for_model(SchemeMap)
        try:
            return Access.objects.filter(
                Q(
                    object_type=map_content_type,
                    object_id=self._map.pk,
                ) |
                Q(
                    object_type=scheme_content_type,
                    object_id=self._map.scheme.pk,
                ),
            ).filter(
                user=self.cleaned_data['current_user'],
            )
        except Access.DoesNotExist:
            return None

    def access_presence(self) -> None:
        if self._map:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the scheme id = '
                                                                f'{self._map.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN

    def map_presence(self) -> None:
        if not self._map:
            self.add_error(
                "map_id",
                NotFound(
                    f"Map id={self.cleaned_data['filter_map_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND
