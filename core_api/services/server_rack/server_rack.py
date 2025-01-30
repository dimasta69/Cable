from django import forms
from functools import lru_cache

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status

from models_app.models import User, Access, Scheme, ServerRack
from utils.fields import ModelField
from utils.services import ServiceWithResult


class ServerRackService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)

    custom_validations = ['server_rack_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._server_rack
            self.response_status = status.HTTP_200_OK
        return self

    @property
    @lru_cache()
    def _server_rack(self) -> ServerRack | None:
        try:
            return ServerRack.objects.get(id=self.cleaned_data['id'])
        except ServerRack.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        try:
            return Access.objects.get(
                user=self.cleaned_data['current_user'],
                object_type=self.scheme_content_type,
                object_id=self._server_rack.room.building.scheme.pk,
            )
        except Access.DoesNotExist:
            return None

    def server_rack_presence(self) -> None:
        if not self._server_rack:
            self.add_error('id', ObjectDoesNotExist(f'Server rack id={self.cleaned_data["id"]} '
                                                    'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if self._server_rack:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._server_rack.room.building.scheme.id} '
                                                                'is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
