from functools import lru_cache
from django import forms
from django.core.exceptions import ValidationError
from rest_framework import status

from core_api.utils.access_checker import scope_for_room
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from models_app.models import User, Equipment, Room
from utils.fields import ModelField
from utils.services import ServiceWithResult


class UpdateRoomService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    number = forms.CharField(required=False)
    is_server_room = forms.BooleanField(required=False)
    current_user = ModelField(User)
    floor = forms.IntegerField(required=False)
    equipment_id = forms.IntegerField(required=False)

    custom_validations = ['run_presence_checks', 'access_presence', 'equipment_presence']
    presence_checks = [("_room", "id", "Room")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_room
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _update_room(self) -> Room:
        room = self._room
        if self.cleaned_data['number']:
            room.number = self.cleaned_data['number']
        if self.cleaned_data['is_server_room']:
            room.is_server_room = self.cleaned_data['is_server_room']
        if self.cleaned_data["floor"]:
            room.floor = self.cleaned_data["floor"]
        if self.cleaned_data['equipment_id']:
            self._equipment.room = room
            self._equipment.save()
        room.save()
        return room

    def get_access_scope(self):
        return scope_for_room(self._room)

    @property
    @lru_cache()
    def _room(self) -> Room:
        try:
            return Room.objects.select_related("building").get(id=self.cleaned_data['id'])
        except Room.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _equipment(self) -> Equipment:
        try:
            return Equipment.objects.get(id=self.cleaned_data.get('equipment_id'))
        except Equipment.DoesNotExist:
            return None

    def equipment_presence(self) -> None:
        if self.cleaned_data['equipment_id'] and self._equipment is None:
            self.add_error('equipment_id', ObjectDoesNotExist(f'Equipment if={self.cleaned_data["equipment_id"]}'
                                                              ' not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
        elif self.cleaned_data['equipment_id'] and self._equipment:
            if getattr(self._equipment, "units", None) or self._equipment.room is None:
                self.add_error('equipment_id', ValidationError(f'Equipment if={self.cleaned_data["equipment_id"]}'
                                                               'stands in a rack'))
                self.response_status = status.HTTP_400_BAD_REQUEST
