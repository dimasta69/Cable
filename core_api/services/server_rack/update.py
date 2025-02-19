from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from functools import lru_cache

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status

from models_app.models import User, Access, ServerRack, Scheme, Building, Room
from utils.fields import ModelField
from utils.services import ServiceWithResult


class UpdateServerRackService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    title = forms.CharField(required=False)
    max_power = forms.IntegerField(required=False)
    current_user = ModelField(User)

    custom_validations = ['server_rack_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_server_rack
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _update_server_rack(self) -> ServerRack:
        server_rack = self._server_rack
        if self.cleaned_data['title']:
            server_rack.title = self.cleaned_data['title']
        if self.cleaned_data['max_power']:
            server_rack.max_power = self.cleaned_data['max_power']
        server_rack.save()
        return server_rack

    @property
    @lru_cache()
    def _server_rack(self) -> ServerRack | None:
        try:
            return ServerRack.objects.get(id=self.cleaned_data['id'])
        except ServerRack.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        building_content_type = ContentType.objects.get_for_model(Building)
        room_content_type = ContentType.objects.get_for_model(Room)
        try:
            return (Access.objects.filter(
                Q(
                    object_type=scheme_content_type,
                    object_id=self._server_rack.room.building.id,
                )|
                Q(
                    object_type=building_content_type,
                    object_id=self._server_rack.room.building.scheme.id,
                )|
                Q(
                    object_type=room_content_type,
                    object_id=self._server_rack.room.id,
                ),
            ).filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator'],
            ))
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
