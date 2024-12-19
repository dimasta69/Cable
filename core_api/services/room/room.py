from functools import lru_cache
from django import forms
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status

from models_app.models import Access, User
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Room


class RoomService(ServiceWithResult):
    current_user = ModelField(User)
    id = forms.IntegerField(required=True)

    custom_validations = ['room_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._room
            self.response_status = status.HTTP_200_OK
        return self

    @property
    @lru_cache()
    def _room(self):
        try:
            return Room.objects.select_related("building", 'building__scheme').get(id=self.cleaned_data['id'])
        except Room.DoesNotExist:
            return None

    @property
    def access(self):
        try:
            return Access.objects.get(user=self.cleaned_data['current_user'], scheme=self._room.building.scheme)
        except Access.DoesNotExist:
            return None

    def room_presence(self):
        if self.cleaned_data['id']:
            if not self._room:
                self.add_error('room_id', ObjectDoesNotExist('Room id='
                                                             f'{self.cleaned_data["id"]} '
                                                             'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self):
        if self._room:
            if not self.access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._room.building.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
