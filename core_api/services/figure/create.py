from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework import status

from typing import List

from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Figure, User, Scheme, SchemeMap, Access
from models_app.models.schemes.figure.models import type_choice


class CreateFigureService(ServiceWithResult):
    current_user = ModelField(User)
    map_id = forms.IntegerField(required=True)
    title = forms.CharField(required=True)
    type = forms.CharField(required=True)
    x = forms.FloatField(required=True)
    y = forms.FloatField(required=True)
    width = forms.IntegerField(min_value=1)
    height = forms.IntegerField(min_value=1)

    custom_validations = ["access_presence", "map_presence", "type_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_figure
        return self

    @property
    def _create_figure(self) -> Figure:
        return Figure.objects.create(
            schemes=self._map,
            type=self.cleaned_data['type'],
            x=self.cleaned_data['x'],
            y=self.cleaned_data['y'],
            width=self.cleaned_data['width'],
            height=self.cleaned_data['height'],
        )

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
                role__in=['Change', 'Creator']
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
                    f"Map id={self.cleaned_data['map_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def type_presence(self) -> None:
        if not [t[0] for t in type_choice if t[0] == self.cleaned_data['type']]:
            self.add_error(
                "map_id",
                NotFound(
                    f"Type ={self.cleaned_data['type']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND
