from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from typing import List

from core_api.utils.presence import PresenceChecksMixin
from utils.services import ServiceWithResult
from django import forms
from functools import lru_cache
from models_app.models import User, Building, Room, ServerRack, SchemeMap, Vlan, Segment, Equipment
from utils.fields import ModelField
from models_app.models import Scheme
from models_app.models import Access
from django.db.models import Q


class UsersListServices(PresenceChecksMixin, ServiceWithResult):
    page = forms.IntegerField(required=False)
    current_user = ModelField(User)
    per_page = forms.IntegerField(required=False)
    search_filter = forms.CharField(required=False)
    order_by = forms.CharField(required=False)
    scheme_id = forms.IntegerField(required=True)
    filter_building_id = forms.IntegerField(required=False)
    filter_room_id = forms.IntegerField(required=False)
    filter_map_id = forms.IntegerField(required=False)
    filter_server_rack_id = forms.IntegerField(required=False)
    filter_equipment_id = forms.IntegerField(required=False)
    filter_segment_id = forms.IntegerField(required=False)
    filter_vlan_id = forms.IntegerField(required=False)

    custom_validations = [
        'run_presence_checks',
        'order_presence',
    ]
    presence_checks = [
        ("_scheme", "scheme_id", "Scheme"),
        ("_building", "filter_building_id", "Building", True),
        ("_room", "filter_room_id", "Room", True),
        ("_server_rack", "filter_server_rack_id", "Server rack", True),
        ("_map", "filter_map_id", "Map", True),
        ("_equipment", "filter_equipment_id", "Equipment", True),
        ("_segment", "filter_segment_id", "Segment", True),
        ("_vlan", "filter_vlan_id", "Vlan", True),
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._scheme_list_filter
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _scheme_list_filter(self) -> List[User]:
        user_list = self._users
        if self.cleaned_data['filter_building_id']:
            user_list = user_list.access.filter(
                object_type=ContentType.objects.get_for_model(Building),
                object_id=self.cleaned_data['filter_building_id'],
            )
        if self.cleaned_data['filter_room_id']:
            user_list = user_list.access.filter(
                object_type=ContentType.objects.get_for_model(Room),
                object_id=self.cleaned_data['filter_room_id'],
            )
        if self.cleaned_data['filter_map_id']:
            user_list = user_list.access.filter(
                object_type=ContentType.objects.get_for_model(SchemeMap),
                object_id=self.cleaned_data['filter_map_id'],
            )
        if self.cleaned_data['filter_server_rack_id']:
            user_list = user_list.access.filter(
                object_type=ContentType.objects.get_for_model(ServerRack),
                object_id=self.cleaned_data['filter_server_rack_id'],
            )
        if self.cleaned_data['filter_equipment_id']:
            user_list = user_list.access.filter(
                object_type=ContentType.objects.get_for_model(Equipment),
                object_id=self.cleaned_data['filter_equipment_id'],
            )
        if self.cleaned_data['filter_segment_id']:
            user_list = user_list.access.filter(
                object_type=ContentType.objects.get_for_model(Segment),
                object_id=self.cleaned_data['filter_segment_id'],
            )
        if self.cleaned_data['filter_vlan_id']:
            user_list = user_list.access.filter(
                object_type=ContentType.objects.get_for_model(Vlan),
                object_id=self.cleaned_data['filter_vlan_id'],
            )
        if self.cleaned_data['order_by']:
            user_list = user_list.order_by(self.cleaned_data['order_by'])
        if self.cleaned_data['search_filter']:
            user_list = user_list.filter(
                Q(username__icontains=self.cleaned_data['search_filter'])
            )
        return user_list

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data['scheme_id'])
        except Scheme.DoesNotExist:
            return None

    @property
    def _users(self) -> List[User]:
        try:
            return User.objects.all().prefetch_related("access")
        except User.DoesNotExist:
            return User.objects.none()

    @property
    def _access(self) -> List[Access]:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        try:
            return Access.objects.filter(
                object_type=scheme_content_type,
                object_id=self._scheme.pk,
            ).values_list('user__id', flat=True)
        except Access.DoesNotExist:
            return Access.objects.none()

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.get(id=self.cleaned_data['filter_equipment_id'])
        except Equipment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _segment(self) -> Segment | None:
        try:
            return Segment.objects.get(id=self.cleaned_data['filter_segment_id'])
        except Segment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _vlan(self) -> Vlan | None:
        try:
            return Vlan.objects.get(id=self.cleaned_data['filter_vlan_id'])
        except Vlan.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _building(self) -> Building | None:
        try:
            return Building.objects.get(id=self.cleaned_data['filter_building_id'])
        except Building.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _room(self) -> Room | None:
        try:
            return Room.objects.get(id=self.cleaned_data['filter_room_id'])
        except Room.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _server_rack(self) -> ServerRack | None:
        try:
            return ServerRack.objects.get(id=self.cleaned_data['filter_server_rack_id'])
        except ServerRack.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _map(self) -> SchemeMap | None:
        try:
            return SchemeMap.objects.get(id=self.cleaned_data['filter_map_id'])
        except SchemeMap.DoesNotExist:
            return None

    def order_presence(self) -> None:
        if self.cleaned_data['order_by']:
            if not self.cleaned_data['order_by'] in ['username', '-username']:
                self.add_error('order_by', ObjectDoesNotExist(f'Order {self.cleaned_data["order_by"]} is not found'))
                self.response_status = status.HTTP_404_NOT_FOUND
