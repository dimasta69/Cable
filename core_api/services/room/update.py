from functools import lru_cache
from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied
from rest_framework import status

from models_app.models import Access, User
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Room
from models_app.models import Building


class UpdateRoomService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    number = forms.CharField(required=False)
    is_server_room = forms.BooleanField(required=False)
    current_user = ModelField(User)
    # equipment =

    custom_validations = ['room_presence', 'number_presence', 'access_presence']

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
        if self.cleaned_data['is_server_room']:
            room.is_server_room = self.cleaned_data['is_server_room']
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

    @property
    def access(self):
        try:
            return Access.objects.get(user=self.cleaned_data['current_user'], scheme=self.room.building.scheme,
                                      role__in=['Change', 'Creator'])
        except Access.DoesNotExist:
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

    def access_presence(self):
        if self.room:
            if not self.access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.room.building.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
