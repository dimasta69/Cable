from functools import lru_cache
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from core_api.utils.access_checker import scope_for_building
from core_api.utils.scheme_access import ResourceAccessMixin
from models_app.models import User, Building, Room
from utils.fields import ModelField
from utils.services import ServiceWithResult


class CreateRoomService(ResourceAccessMixin, ServiceWithResult):
    building_id = forms.IntegerField(required=True)
    number = forms.CharField(required=True)
    is_server_room = forms.BooleanField(required=False)
    floor = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['building_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_room
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def _create_room(self) -> Room:
        return Room.objects.create(
            building=self._building, number=self.cleaned_data['number'],
            is_server_room=self.cleaned_data.get('is_server_room'),
            floor=self.cleaned_data.get('floor')
        )

    def get_access_scope(self):
        return scope_for_building(self._building)

    @property
    @lru_cache()
    def _building(self) -> Building | None:
        try:
            return Building.objects.select_related("scheme").get(id=self.cleaned_data['building_id'])
        except Building.DoesNotExist:
            return None

    def building_presence(self) -> None:
        if self.cleaned_data['building_id']:
            if not self._building:
                self.add_error('building_id', ObjectDoesNotExist('Building id='
                                                                 f'{self.cleaned_data["building_id"]} '
                                                                 'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND
