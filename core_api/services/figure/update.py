from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework import status

from typing import List

from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Figure, User, Scheme, SchemeMap, Access


class UpdateFigureService(ServiceWithResult):
    current_user = ModelField(User)
    id = forms.IntegerField(required=True)
    title = forms.CharField(required=False)
    x = forms.FloatField(required=False)
    y = forms.FloatField(required=False)
    width = forms.IntegerField(min_value=1, required=False)
    height = forms.IntegerField(min_value=1, required=False)

    custom_validations = ["access_presence", "figure_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_figure
        return self

    @property
    def _update_figure(self) -> Figure:
        if self.cleaned_data['title']:
            self._figure.title = self.cleaned_data['title']
        if self.cleaned_data['x']:
            self._figure.x = self.cleaned_data['x']
        if self.cleaned_data['y']:
            self._figure.y = self.cleaned_data['y']
        if self.cleaned_data['width']:
            self._figure.width = self.cleaned_data['width']
        if self.cleaned_data['height']:
            self._figure.height = self.changed_data['height']
        self._figure.save()
        return self._figure

    @property
    def _figure(self) -> Figure | None:
        try:
            return Figure.objects.get(id=self.cleaned_data['id'])
        except Figure.DoesNotExist:
            return None

    @property
    def _access(self) -> List[Access] | None:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        map_content_type = ContentType.objects.get_for_model(SchemeMap)
        try:
            return Access.objects.filter(
                Q(
                    object_type=map_content_type,
                    object_id=self._figure.schemes.pk,
                ) |
                Q(
                    object_type=scheme_content_type,
                    object_id=self._figure.schemes.scheme.pk,
                ),
            ).filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator']
            )
        except Access.DoesNotExist:
            return None

    def access_presence(self) -> None:
        if self._figure:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the scheme id = '
                                                                f'{self._figure.schemes.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN

    def figure_presence(self) -> None:
        if not self._figure:
            self.add_error(
                "id",
                NotFound(
                    f"Figure id={self.cleaned_data['id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND
