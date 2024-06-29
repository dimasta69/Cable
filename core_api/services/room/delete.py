from functools import lru_cache
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.room import Room


class DeleteRoomService(ServiceWithResult):
    id = forms.IntegerField(required=True)

    custom_validations = ['room_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.delete_room
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    @property
    def delete_room(self):
        self.room.delete()
        return None

    @property
    @lru_cache()
    def room(self):
        try:
            return Room.objects.get(id=self.cleaned_data['id'])
        except Room.DoesNotExist:
            return None

    def room_presence(self):
        if not self.room:
            self.add_error('id', ObjectDoesNotExist(f'Room id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
