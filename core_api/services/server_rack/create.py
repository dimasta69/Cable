from django import forms
from functools import lru_cache
from django.db.models import Q

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status

from models_app.models import User, Access, Scheme, ServerRack, Room, Building
from utils.fields import ModelField
from utils.services import ServiceWithResult


class CreateServerRackService(ServiceWithResult):
    number_of_units = forms.IntegerField(required=True)
    room_id = forms.IntegerField(required=True)
    title = forms.CharField(required=False)
    max_power = forms.IntegerField(required=False)
    current_user = ModelField(User)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)
    building_content_type = ContentType.objects.get_for_model(Building)
    room_content_type = ContentType.objects.get_for_model(Room)

    custom_validations = ['room_presence', 'room_server_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_server_rack
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def _create_server_rack(self) -> ServerRack:
        server_rack = ServerRack.objects.create(
            number_of_units=self.cleaned_data['number_of_units'],
            room=self._room,
            title=self.cleaned_data['title'],
            max_power=self.cleaned_data['max_power']
        )
        return server_rack

    @property
    @lru_cache()
    def _room(self) -> Room | None:
        try:
            return Room.objects.select_related(
                "building",
                "building__scheme",
            ).get(id=self.cleaned_data['room_id'])
        except Room.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        try:
            return (Access.objects.filter(
                Q(
                    object_type=self.scheme_content_type,
                    object_id=self._room.building.scheme.id,
                ),
                Q(
                    object_type=self.building_content_type,
                    object_id=self._room.building.id,
                ),
                Q(
                    object_type=self.room_content_type,
                    object_id=self._room.id,
                ),
            ).filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator'],
            ))
        except Access.DoesNotExist:
            return None

    def room_presence(self) -> None:
        if not self._room:
            self.add_error('room_id', ObjectDoesNotExist('Room id='
                                                         f'{self.cleaned_data["room_id"]} '
                                                         'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def room_server_presence(self) -> None:
        if self._room:
            if not self._room.is_server_room:
                self.add_error('room_id', ObjectDoesNotExist('Room id='
                                                             f'{self.cleaned_data["room_id"]} '
                                                             'is not server'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def access_presence(self) -> None:
        if self._room:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._room.building.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
