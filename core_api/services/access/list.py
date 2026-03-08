from functools import lru_cache
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet
from rest_framework import status
from typing import List, Any
from django.core.paginator import Paginator, EmptyPage, Page
from cabel.settings import REST_FRAMEWORK

from core_api.utils.presence import PresenceChecksMixin
from models_app.models import Access, User, Scheme, Building, Room, ServerRack, SchemeMap, Equipment, Segment, Vlan
from utils.fields import ModelField
from utils.services import ServiceWithResult


def _access(object_type: ContentType, uid: int) -> QuerySet[Access, Access]:
    try:
        return Access.objects.filter(
            object_type=object_type,
            object_id=uid,
            role="Change",
        )
    except Access.DoesNotExist:
        return Access.objects.none()


class AccessListService(PresenceChecksMixin, ServiceWithResult):
    current_user = ModelField(User)
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    filter_scheme_id = forms.IntegerField(required=True)
    filter_building_id = forms.IntegerField(required=False)
    filter_room_id = forms.IntegerField(required=False)
    filter_map_id = forms.IntegerField(required=False)
    filter_server_rack_id = forms.IntegerField(required=False)
    filter_equipment_id = forms.IntegerField(required=False)
    filter_segment_id = forms.IntegerField(required=False)
    filter_vlan_id = forms.IntegerField(required=False)
    search_filter = forms.CharField(required=False)

    custom_validations = [
        'run_presence_checks',
        'access_owner_or_superuser',
    ]
    presence_checks = [
        ("_scheme", "filter_scheme_id", "Scheme"),
        ("_building", "filter_building_id", "Building", True),
        ("_room", "filter_room_id", "Room", True),
        ("_server_rack", "filter_server_rack_id", "Server rack", True),
        ("_map", "filter_map_id", "Map", True),
        ("_equipment", "filter_equipment_id", "Equipment", True),
        ("_segment", "filter_segment_id", "Segment", True),
        ("_vlan", "filter_vlan_id", "Vlan", True),
    ]

    def process(self) -> "AccessListService":
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.access_pagination
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def access_pagination(self) -> Page[Any]:
        try:
            return (Paginator(self._access_filter_list, per_page=(self.cleaned_data['per_page'] or
                                                                  REST_FRAMEWORK['PAGE_SIZE'])).
                    page(self.cleaned_data['page'] or 1))
        except EmptyPage:
            return (Paginator(self._access_filter_list, per_page=(self.cleaned_data['per_page'] or
                                                                  REST_FRAMEWORK['PAGE_SIZE'])).page(1))

    @property
    def _access_filter_list(self) -> List[Access]:
        access_list = self._list_acc
        scheme_content_type = ContentType.objects.get_for_model(Scheme)

        if self.cleaned_data["filter_building_id"]:
            access_filter = _access(
                ContentType.objects.get_for_model(Building), self._building.pk,
            )
            access_list = access_filter | access_list.exclude(
                role="Read", object_type=scheme_content_type, user__id__in=access_list.values("user__id")
            ) if access_filter else access_list

        if self.cleaned_data["filter_room_id"]:
            access_filter = _access(
                ContentType.objects.get_for_model(Room), self._room.pk,
            )
            access_list = access_filter | access_list.exclude(
                role="Read", object_type=scheme_content_type, user__id__in=access_list.values("user__id")
            ) if access_filter else access_list

        if self.cleaned_data["filter_map_id"]:
            access_filter = _access(
                ContentType.objects.get_for_model(SchemeMap), self._map.pk,
            )
            access_list = access_filter | access_list.exclude(
                role="Read", object_type=scheme_content_type, user__id__in=access_list.values("user__id")
            ) if access_filter else access_list

        if self.cleaned_data["filter_server_rack_id"]:
            access_filter = _access(
                ContentType.objects.get_for_model(ServerRack), self._server_rack.pk,
            )
            access_list = access_filter | access_list.exclude(
                role="Read", object_type=scheme_content_type, user__id__in=access_list.values("user__id")
            ) if access_filter else access_list

        if self.cleaned_data["filter_equipment_id"]:
            access_filter = _access(
                ContentType.objects.get_for_model(Equipment), self._equipment.pk,
            )
            access_list = access_filter | access_list.exclude(
                role="Read", object_type=scheme_content_type, user__id__in=access_list.values("user__id")
            ) if access_filter else access_list

        if self.cleaned_data["filter_segment_id"]:
            access_filter = _access(
                ContentType.objects.get_for_model(Segment), self._segment.pk,
            )
            access_list = access_filter | access_list.exclude(
                role="Read", object_type=scheme_content_type, user__id__in=access_list.values("user__id")
            ) if access_filter else access_list

        if self.cleaned_data["filter_vlan_id"]:
            access_filter = _access(
                ContentType.objects.get_for_model(Vlan), self._vlan.pk,
            )
            access_list = access_filter | access_list.exclude(
                role="Read", object_type=scheme_content_type, user__id__in=access_list.values("user__id")
            ) if access_filter else access_list

        if self.cleaned_data['search_filter']:
            access_list = access_list.filter(
                Q(user__username__icontains=self.cleaned_data['search_filter'])
            )
        return access_list

    @property
    @lru_cache()
    def _list_acc(self) -> List[Access]:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        try:
            return Access.objects.filter(
                object_type=scheme_content_type,
                object_id=self._scheme.id,
                role="Read",
            )
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
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data['filter_scheme_id'])
        except Scheme.DoesNotExist:
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

    def access_owner_or_superuser(self) -> None:
        if self._scheme and self._list_acc:
            if (self._scheme.creator != self.cleaned_data['current_user']
                    and not self.cleaned_data['current_user'].is_superuser):
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._scheme.pk} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
