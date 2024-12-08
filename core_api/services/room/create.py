from functools import lru_cache
from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied
from rest_framework import status

from models_app.models import Access, User
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Room
from models_app.models import Building


class CreateRoomService(ServiceWithResult):
    building_id = forms.IntegerField(required=True)
    number = forms.CharField(required=True)
    type = forms.CharField(required=True)
    current_user = ModelField(User)

    custom_validations = ['building_presence', 'type_presence', 'number_presence', 'access_presence']

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

    @property
    def access(self):
        try:
            return Access.objects.get(user=self.cleaned_data['current_user'], scheme=self.building.scheme,
                                      role__in=['Change', 'Creator'])
        except Access.DoesNotExist:
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

    def access_presence(self):
        if self.building:
            if not self.access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.building.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
