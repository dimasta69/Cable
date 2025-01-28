from functools import lru_cache
from django import forms
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status

from models_app.models import User, Access
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Room


class DeleteRoomService(ServiceWithResult):
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

    @property
    @lru_cache()
    def _room(self) -> Room | None:
        try:
            return Room.objects.get(id=self.cleaned_data['id'])
        except Room.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        try:
            return Access.objects.get(user=self.cleaned_data['current_user'], scheme=self._room.building.scheme,
                                      role__in=['Change', 'Creator'])
        except Access.DoesNotExist:
            return None

    def room_presence(self) -> None:
        if not self._room:
            self.add_error('id', ObjectDoesNotExist(f'Room id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if self._room:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._room.building.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
