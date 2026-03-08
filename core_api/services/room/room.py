from functools import lru_cache
from django import forms
from rest_framework import status

from core_api.utils.access_checker import AccessChecker, scope_for_room
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from models_app.models import User, Room
from utils.fields import ModelField
from utils.services import ServiceWithResult


class RoomService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    current_user = ModelField(User)
    id = forms.IntegerField(required=True)

    access_required_roles = AccessChecker.ROLES_READ
    custom_validations = ['run_presence_checks', 'access_presence']
    presence_checks = [{"obj_attr": "_room", "field_name": "id", "model_label": "Room", "error_field": "room_id"}]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._room
            self.response_status = status.HTTP_200_OK
        return self

    def get_access_scope(self):
        return scope_for_room(self._room)

    @property
    @lru_cache()
    def _room(self) -> Room | None:
        try:
            return Room.objects.select_related("building", 'building__scheme').get(id=self.cleaned_data['id'])
        except Room.DoesNotExist:
            return None
