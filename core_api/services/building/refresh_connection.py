from django import forms
from rest_framework.exceptions import NotFound
from rest_framework import status
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType

from functools import lru_cache
from utils.services import ServiceWithResult
from core_api.utils.refresh_connection_building import refresh_connection_building
from models_app.models import Scheme, User, Access
from utils.fields import ModelField


class RefreshBuildingConnectionService(ServiceWithResult):
    scheme_id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ["access_presence", "scheme_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._refresh_connection_buildings()
        return self

    def _refresh_connection_buildings(self) -> None:
        refresh_connection_building(self._scheme)

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.prefetch_related("buildings").get(id=self.cleaned_data['scheme_id'])
        except Scheme.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        try:
            return Access.objects.get(
                user=self.cleaned_data['current_user'],
                object_type=scheme_content_type,
                object_id=self._scheme.pk,
            )
        except Access.DoesNotExist:
            return None

    def scheme_presence(self) -> None:
        if not self._scheme:
            self.add_error(
                "scheme_id",
                NotFound(
                    f"Scheme id={self.cleaned_data['scheme_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if self._scheme:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.cleaned_data["filter_scheme_id"]} is '
                                                                'not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
