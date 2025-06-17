from functools import lru_cache

from django import forms
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from models_app.models import Equipment, Room, Access, Scheme, Building, User
from utils.fields import ModelField
from utils.services import ServiceWithResult


class AddEquipmentFromRoomService(ServiceWithResult):
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
    def _connection_to_room(self) -> None:
        equipment = self._equipment
        equipment.room = self._room
        equipment.save()
        return equipment

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.get(id=self.cleaned_data['equipment_id'])
        except Equipment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _room(self) -> Room | None:
        try:
            return Room.objects.get(id=self.cleaned_data['room_id'])
        except Room.DoesNotExist:
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
                    object_id=self._room.building.id,
                )|
                Q(
                    object_type=building_content_type,
                    object_id=self._room.building.scheme.id,
                )|
                Q(
                    object_type=room_content_type,
                    object_id=self._room.id,
                ),
            ).filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator'],
            ))
        except Access.DoesNotExist:
            return None

    def equipment_presence(self) -> None:
        if not self._equipment:
            self.add_error('id', ObjectDoesNotExist(f"Equipment id ={self.cleaned_data['equipment_id']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def room_presence(self) -> None:
        if not self._room:
            self.add_error('id', ObjectDoesNotExist(f"Room id ={self.cleaned_data['room_id']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def equipment_room_null(self) -> None:
        if self._equipment and self._equipment.room:
            self.add_error('id', ObjectDoesNotExist(f"Equipment id ={self.cleaned_data['equipment_id']} "
                                                    "already standing in the room"))
            self.response_status = status.HTTP_400_BAD_REQUEST

    def access_presence(self) -> None:
        if self._room:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._room.building.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
