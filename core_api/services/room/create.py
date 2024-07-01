from functools import lru_cache
from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.room import Room
from models_app.models.building import Building


class CreateRoomService(ServiceWithResult):
    building_id = forms.IntegerField(required=True)
    number = forms.CharField(required=True)
    type = forms.CharField(required=True)

    custom_validations = ['building_presence', 'type_presence', 'number_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.create_room
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def create_room(self):
        return Room.objects.create(building=self.building, number=self.cleaned_data['number'],
                                   type=self.cleaned_data['type'])

    @property
    def room_list(self):
        try:
            return Room.objects.all()
        except Room.DoesNotExist:
            return Room.objects.none()

    @property
    @lru_cache()
    def building(self):
        try:
            return Building.objects.get(id=self.cleaned_data['building_id'])
        except Building.DoesNotExist:
            return None

    def type_presence(self):
        if self.cleaned_data['type']:
            if not any(type_tuple[1] == self.cleaned_data['type'] for type_tuple in Room.TYPE_ROOM_CHOICES):
                self.add_error('filter_type', ObjectDoesNotExist('Type ='
                                                                 f'{self.cleaned_data["type"]} '
                                                                 f'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def building_presence(self):
        if self.cleaned_data['building_id']:
            if not self.building:
                self.add_error('building_id', ObjectDoesNotExist('Building id='
                                                                 f'{self.cleaned_data["building_id"]} '
                                                                 'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def number_presence(self):
        for room in self.room_list:
            if room.number == self.cleaned_data['number']:
                self.add_error('model', ValidationError(f'Field with number={self.cleaned_data["number"]}'
                                                        ' already exists'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
