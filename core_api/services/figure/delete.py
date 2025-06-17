from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework import status

from typing import List

from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Figure, User, Scheme, SchemeMap, Access


class DeleteFigureService(ServiceWithResult):
    current_user = ModelField(User)
    id = forms.IntegerField(required=True)

    custom_validations = ["access_presence", "figure_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._delete_figure()
        return self

    def _delete_figure(self) -> None:
        self._figure.delete()

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
