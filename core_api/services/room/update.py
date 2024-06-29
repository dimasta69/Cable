from functools import lru_cache
from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.room import Room
from models_app.models.building import Building


class UpdateRoomService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    number = forms.CharField(required=False)

    custom_validations = ['room_presence', 'number_presence', ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.update_room
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def update_room(self):
        room = self.room
        if self.cleaned_data['number']:
            room.number = self.cleaned_data['number']
        room.save()
        return room

    @property
    @lru_cache()
    def room(self):
        try:
            return Room.objects.get(id=self.cleaned_data['id'])
        except Room.DoesNotExist:
            return None

    @property
    def room_list(self):
        try:
            return Room.objects.filter(building__scheme=self.room.building.scheme)
        except Room.DoesNotExist:
            return None

    @property
    @lru_cache()
    def building(self):
        try:
            return Building.objects.get(id=self.room.building.id)
        except Building.DoesNotExist:
            return None

    def room_presence(self):
        if not self.room:
            self.add_error('id', ObjectDoesNotExist(f'Room id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def number_presence(self):
        if self.cleaned_data['number'] and self.room:
            for room in self.room_list:
                if room.number == self.cleaned_data['number']:
                    self.add_error('model', ValidationError(f'Field with number={self.cleaned_data["number"]}'
                                                            ' already exists'))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
