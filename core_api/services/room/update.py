from functools import lru_cache
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied
from rest_framework import status
from django.db.models import Q

from models_app.models import Access, User, Scheme, Building
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Equipment, Room


class UpdateRoomService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    number = forms.CharField(required=False)
    is_server_room = forms.BooleanField(required=False)
    current_user = ModelField(User)
    floor = forms.IntegerField(required=False)
    equipment_id = forms.IntegerField(required=False)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)
    building_content_type = ContentType.objects.get_for_model(Building)

    custom_validations = ['room_presence', 'access_presence', 'equipment_presence']

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
                )
            ).filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator'],
            ))
        except Access.DoesNotExist:
            return None

    def room_presence(self) -> None:
        if not self._room:
            self.add_error('id', ObjectDoesNotExist(f'Room id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

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

    def access_presence(self) -> None:
        if self._room:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._room.building.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
