from django import forms
from functools import lru_cache

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status
from django.contrib.contenttypes.models import ContentType

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Scheme, Building, Room, ServerRack, SchemeMap, Vlan, Segment, Equipment
from models_app.models import User
from models_app.models import Access


class CreateAccessService(ServiceWithResult):
    scheme_id = forms.IntegerField(required=True)
    user_id = forms.IntegerField(required=True)
    building_id = forms.IntegerField(required=False)
    room_id = forms.IntegerField(required=False)
    map_id = forms.IntegerField(required=False)
    server_rack_id = forms.IntegerField(required=False)
    equipment_id = forms.IntegerField(required=False)
    vlan_id = forms.IntegerField(required=False)
    segment_id = forms.IntegerField(required=False)
    role = forms.CharField(required=True)
    current_user = ModelField(User)

    custom_validations = [
        'scheme_presence',
        'role_presence',
        'user_presence',
        'access_owner_or_superuser',
        'building_presence',
        'room_presence',
        'server_rack_presence',
        'map_presence',
        'equipment_presence',
        'vlan_presence',
        'segment_presence',
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_access
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def _create_access(self) -> Access:
        object_mapping = {
            "building_id": (Building, self._building),
            "room_id": (Room, self._room),
            "map_id": (SchemeMap, self._map),
            "server_rack_id": (ServerRack, self._server_rack),
            "equipment_id": (Equipment, self._equipment),
            "vlan_id": (Vlan, self._vlan),
            "segment_id": (Segment, self._segment),
        }

        create_data = {
            "object_type": None,
            "object_id": None
        }

        for key, (model, instance) in object_mapping.items():
            if self.cleaned_data.get(key):
                create_data['object_type'] = ContentType.objects.get_for_model(model)
                create_data['object_id'] = instance.pk
                break

        return Access.objects.create(
            user=self._user,
            role=self.cleaned_data['role'],
            object_type=create_data['object_type'],
            object_id=create_data['object_id'],
        )

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data['scheme_id'])
        except Scheme.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.get(id=self.cleaned_data['equipment_id'])
        except Equipment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _vlan(self) -> Vlan | None:
        try:
            return Vlan.objects.get(id=self.cleaned_data['vlan_id'])
        except Vlan.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _segment(self) -> Segment | None:
        try:
            return Segment.objects.get(id=self.cleaned_data['segment_id'])
        except Segment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _user(self) -> User | None:
        try:
            return User.objects.get(id=self.cleaned_data['user_id'])
        except User.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _building(self) -> Building | None:
        try:
            return Building.objects.get(id=self.cleaned_data['building_id'])
        except Building.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _room(self) -> Room | None:
        try:
            return Room.objects.get(id=self.cleaned_data['room_id'])
        except Room.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _server_rack(self) -> ServerRack | None:
        try:
            return ServerRack.objects.get(id=self.cleaned_data['server_rack_id'])
        except ServerRack.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _map(self) -> SchemeMap | None:
        try:
            return SchemeMap.objects.get(id=self.cleaned_data['map_id'])
        except SchemeMap.DoesNotExist:
            return None

    def scheme_presence(self) -> None:
        if not self._scheme:
            self.add_error('scheme_id', ObjectDoesNotExist('Scheme id='
                                                                  f'{self.cleaned_data["scheme_id"]} '
                                                                  'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def equipment_presence(self) -> None:
        if self.cleaned_data['equipment_id']:
            if not self._equipment:
                self.add_error('equipment_id', ObjectDoesNotExist('Equipment id='
                                                                      f'{self.cleaned_data["equipment_id"]} '
                                                                      'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def vlan_presence(self) -> None:
        if self.cleaned_data['vlan_id']:
            if not self._vlan:
                self.add_error('vlan_id', ObjectDoesNotExist('Vlan id='
                                                                      f'{self.cleaned_data["vlan_id"]} '
                                                                      'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def segment_presence(self) -> None:
        if self.cleaned_data['segment_id']:
            if not self._segment:
                self.add_error('segment_id', ObjectDoesNotExist('Segment id='
                                                                      f'{self.cleaned_data["segment_id"]} '
                                                                      'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def building_presence(self) -> None:
        if self.cleaned_data['building_id']:
            if not self._building:
                self.add_error('building_id', ObjectDoesNotExist('Building id='
                                                                        f'{self.cleaned_data["building_id"]} '
                                                                        'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def room_presence(self) -> None:
        if self.cleaned_data['room_id']:
            if not self._room:
                self.add_error('room_id', ObjectDoesNotExist('Room id='
                                                                    f'{self.cleaned_data["room_id"]} '
                                                                    'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def server_rack_presence(self) -> None:
        if self.cleaned_data['server_rack_id']:
            if not self._server_rack:
                self.add_error('server_rack_id', ObjectDoesNotExist('Server rack id='
                                                                           f'{self.cleaned_data["server_rack_id"]} '
                                                                           'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def map_presence(self) -> None:
        if self.cleaned_data['map_id']:
            if not self._map:
                self.add_error('map_id', ObjectDoesNotExist('Map id='
                                                                   f'{self.cleaned_data["map_id"]} '
                                                                   'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def user_presence(self) -> None:
        if not self._user:
            self.add_error('user_id', ObjectDoesNotExist(f'User id={self.cleaned_data["user_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def role_presence(self) -> None:
        if self.cleaned_data['role']:
            if not self.cleaned_data.get('role') in ['Change', 'Read']:
                self.add_error('filter_role', ObjectDoesNotExist(f"Field in model with "
                                                                 f"{self.cleaned_data['role']} not found"))
                self.response_status = status.HTTP_404_NOT_FOUND

    def access_owner_or_superuser(self) -> None:
        if self._scheme and self._user:
            if (self._scheme.creator != self.cleaned_data['current_user']
                    and not self.cleaned_data['current_user'].is_superuser):
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._scheme.pk} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
