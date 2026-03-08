from django import forms
from functools import lru_cache

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from core_api.utils.access_checker import scope_for_room
from core_api.utils.scheme_access import ResourceAccessMixin
from models_app.models import User, ServerRack, Room
from utils.fields import ModelField
from utils.services import ServiceWithResult


class CreateServerRackService(ResourceAccessMixin, ServiceWithResult):
    number_of_units = forms.IntegerField(required=True)
    room_id = forms.IntegerField(required=True)
    title = forms.CharField(required=False)
    max_power = forms.IntegerField(required=False)
    current_user = ModelField(User)

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

    def get_access_scope(self):
        return scope_for_room(self._room)

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
