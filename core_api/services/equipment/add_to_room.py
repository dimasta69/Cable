from functools import lru_cache

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from core_api.utils.access_checker import scope_for_room
from core_api.utils.scheme_access import ResourceAccessMixin
from models_app.models import Equipment, Room, User
from utils.fields import ModelField
from utils.services import ServiceWithResult


class AddEquipmentFromRoomService(ResourceAccessMixin, ServiceWithResult):
    room_id = forms.IntegerField(required=True)
    equipment_id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ["equipment_presence", "room_presence", "equipment_room_null", "access_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._connection_to_room
        return self

    @property
    def _connection_to_room(self):
        equipment = self._equipment
        equipment.room = self._room
        equipment.save()
        return equipment

    def get_access_scope(self):
        return scope_for_room(self._room)

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.select_related('room', 'room__building').get(
                id=self.cleaned_data['equipment_id']
            )
        except Equipment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _room(self) -> Room | None:
        try:
            return Room.objects.select_related('building', 'building__scheme').get(
                id=self.cleaned_data['room_id']
            )
        except Room.DoesNotExist:
            return None

    def equipment_presence(self) -> None:
        if not self._equipment:
            self.add_error('equipment_id', ObjectDoesNotExist(
                f"Equipment id ={self.cleaned_data['equipment_id']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def room_presence(self) -> None:
        if not self._room:
            self.add_error('room_id', ObjectDoesNotExist(
                f"Room id ={self.cleaned_data['room_id']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def equipment_room_null(self) -> None:
        if self._equipment and self._equipment.room:
            self.add_error('equipment_id', ObjectDoesNotExist(
                f"Equipment id ={self.cleaned_data['equipment_id']} "
                "already standing in the room"))
            self.response_status = status.HTTP_400_BAD_REQUEST
