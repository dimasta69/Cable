from functools import lru_cache
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from core_api.utils.access_checker import scope_for_room
from core_api.utils.scheme_access import ResourceAccessMixin
from models_app.models import User, Room
from utils.fields import ModelField
from utils.services import ServiceWithResult


class DeleteRoomService(ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['room_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._delete_room()
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    def _delete_room(self) -> None:
        self._room.delete()

    def get_access_scope(self):
        return scope_for_room(self._room)

    @property
    @lru_cache()
    def _room(self) -> Room | None:
        try:
            return Room.objects.select_related("building").get(id=self.cleaned_data['id'])
        except Room.DoesNotExist:
            return None

    def room_presence(self) -> None:
        if not self._room:
            self.add_error('id', ObjectDoesNotExist(f'Room id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
