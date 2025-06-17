from functools import lru_cache
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status
from django.db.models import Q

from models_app.models import Access, User
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Building, Room, Scheme


class CreateRoomService(ServiceWithResult):
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

    @property
    @lru_cache()
    def _building(self) -> Building | None:
        try:
            return Building.objects.select_related("scheme").get(id=self.cleaned_data['building_id'])
        except Building.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        building_content_type = ContentType.objects.get_for_model(Building)
        try:
            return (Access.objects.filter(
                Q(
                    object_type=scheme_content_type,
                    object_id=self._building.scheme.id,
                )|
                Q(
                    object_type=building_content_type,
                    object_id=self._building.id,
                )
            ).filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator'],
            ))
        except Access.DoesNotExist:
            return None

    def building_presence(self) -> None:
        if self.cleaned_data['building_id']:
            if not self._building:
                self.add_error('building_id', ObjectDoesNotExist('Building id='
                                                                 f'{self.cleaned_data["building_id"]} '
                                                                 'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if self._building:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._building.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
