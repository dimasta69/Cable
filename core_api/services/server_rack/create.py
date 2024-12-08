from django import forms
from functools import lru_cache

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status

from models_app.models import User, Access
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Room
from models_app.models import ServerRack
from models_app.models import Unit


class CreateServerRackService(ServiceWithResult):
    number_of_units = forms.IntegerField(required=True)
    room_id = forms.IntegerField(required=True)
    title = forms.CharField(required=False)
    max_power = forms.IntegerField(required=False)
    current_user = ModelField(User)

    custom_validations = ['room_presence', 'room_server_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.create_room
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def create_room(self):
        server_rack = ServerRack.objects.create(number_of_units=self.cleaned_data['number_of_units'],
                                                room=self.room,
                                                title=self.cleaned_data['title'],
                                                max_power=self.cleaned_data['max_power'])

        for side in Unit.SIDE_CHOICES:
            for number in range(server_rack.number_of_units):
                Unit.objects.create(uid=number + 1, server_rack=server_rack, side=side[1])
        return server_rack

    @property
    @lru_cache()
    def room(self):
        try:
            return Room.objects.get(id=self.cleaned_data['room_id'])
        except Room.DoesNotExist:
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
            self.add_error('room_id', ObjectDoesNotExist('Room id='
                                                         f'{self.cleaned_data["room_id"]} '
                                                         'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def room_server_presence(self):
        if self.room:
            if not self.room.type == 'Серверная':
                self.add_error('room_id', ObjectDoesNotExist('Room id='
                                                             f'{self.cleaned_data["room_id"]} '
                                                             'is not server'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def access_presence(self):
        if self.room:
            if not self.access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.room.building.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
