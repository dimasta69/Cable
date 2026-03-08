from django import forms
from functools import lru_cache

from django.core.exceptions import PermissionDenied
from rest_framework import status

from core_api.utils.presence import PresenceChecksMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import User, Scheme, Building, Room, ServerRack
from models_app.models import Access


class DeleteAccessService(PresenceChecksMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['access_creator', 'run_presence_checks', 'access_owner_or_superuser']
    presence_checks = [("_access", "id", "Access")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._delete_access()
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    def _delete_access(self) -> None:
        self._access.delete()
        return None

    @property
    @lru_cache()
    def _access(self) -> Access | None:
        try:
            return Access.objects.get(id=self.cleaned_data['id'])
        except Access.DoesNotExist:
            return None

    def access_creator(self) -> None:
        if self._access:
            if self._access.role == 'Creator':
                self.add_error('id', PermissionDenied("You can't delete the creator"))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def access_owner_or_superuser(self) -> None:
        if self._access:
            if (self.creator != self.cleaned_data['current_user']
                    and not self.cleaned_data['current_user'].is_superuser):
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._access.object.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN

    @property
    def creator(self) -> User:
        if isinstance(self._access.object, Scheme):
            return self._access.object.creator
        if isinstance(self._access.object, Building):
            return self._access.object.scheme.creator
        if isinstance(self._access.object, Room):
            return self._access.object.building.scheme.creator
        if isinstance(self._access.object, ServerRack):
            return self._access.object.room.building.scheme.creator
