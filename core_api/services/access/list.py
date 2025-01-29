from functools import lru_cache
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Q
from rest_framework import status
from typing import List

from models_app.models import Access, User, Scheme, Building, Room, ServerRack, SchemeMap
from utils.fields import ModelField
from utils.services import ServiceWithResult



def _access(object_type: ContentType, uid: int) -> List[Access]:
    try:
        return Access.objects.filter(
            object_type=object_type,
            object_id=uid,
            role="Change",
        )
    except Access.DoesNotExist:
        return Access.objects.none()

class AccessListService(ServiceWithResult):
    current_user = ModelField(User)
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    filter_scheme_id = forms.IntegerField(required=True)
    filter_building_id = forms.IntegerField(required=False)
    filter_room_id = forms.IntegerField(required=False)
    filter_map_id = forms.IntegerField(required=False)
    filter_server_rack_id = forms.IntegerField(required=False)
    search_filter = forms.CharField(required=False)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)

    custom_validations = [
        'scheme_presence',
        'access_owner_or_superuser',
        'building_presence',
        'room_presence',
        'server_rack_presence',
        'map_presence',
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._access_filter_list
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _access_filter_list(self) -> List[Access]:
        access_list = self._list_acc
        if self.cleaned_data["filter_building_id"]:
            access_filter = _access(
                ContentType.objects.get_for_model(Building), self._building.pk,
            )
            access_list = access_filter | access_list.exclude(
                role="Read", object_type=self.scheme_content_type, user__id__in=access_list.values("user__id")
            ) if access_filter else access_list
        if self.cleaned_data["filter_room_id"]:
            access_filter = _access(
                ContentType.objects.get_for_model(Room), self._room.pk,
            )
            access_list = access_filter | access_list.exclude(
                role="Read", object_type=self.scheme_content_type, user__id__in=access_list.values("user__id")
            ) if access_filter else access_list
        if self.cleaned_data["filter_map_id"]:
            access_filter = _access(
                ContentType.objects.get_for_model(SchemeMap), self._map.pk,
            )
            access_list = access_filter | access_list.exclude(
                role="Read", object_type=self.scheme_content_type, user__id__in=access_list.values("user__id")
            ) if access_filter else access_list
        if self.cleaned_data["filter_server_rack_id"]:
            access_filter = _access(
                ContentType.objects.get_for_model(ServerRack), self._server_rack.pk,
            )
            access_list = access_filter | access_list.exclude(
                role="Read", object_type=self.scheme_content_type, user__id__in=access_list.values("user__id")
            ) if access_filter else access_list
        if self.cleaned_data['search_filter']:
            access_list = access_list.filter(
                Q(user__username__icontains=self.cleaned_data['search_filter'])             )
        return access_list

    @property
    @lru_cache()
    def _list_acc(self) -> List[Access]:
        try:
            return Access.objects.filter(
                object_type=self.scheme_content_type,
                object_id=self._scheme.id,
                role="Read",
            )
        except Access.DoesNotExist:
            return Access.objects.none()


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
            return SchemeMap.objects.get(id=self.cleaned_data['filter_scheme_map_id'])
        except SchemeMap.DoesNotExist:
            return None

    def scheme_presence(self) -> None:
        if not self._scheme:
            self.add_error('filter_scheme_id', ObjectDoesNotExist('Scheme id='
                                                                  f'{self.cleaned_data["filter_scheme_id"]} '
                                                                      'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def building_presence(self) -> None:
        if self.cleaned_data['filter_building_id']:
            if not self._building:
                self.add_error('filter_building_id', ObjectDoesNotExist('Building id='
                                                                      f'{self.cleaned_data["filter_building_id"]} '
                                                                      'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def room_presence(self) -> None:
        if self.cleaned_data['filter_room_id']:
            if not self._room:
                self.add_error('filter_room_id', ObjectDoesNotExist('Room id='
                                                                      f'{self.cleaned_data["filter_room_id"]} '
                                                                      'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def server_rack_presence(self) -> None:
        if self.cleaned_data['filter_server_rack_id']:
            if not self._server_rack:
                self.add_error('filter_server_rack_id', ObjectDoesNotExist('Server rack id='
                                                                      f'{self.cleaned_data["filter_server_rack_id"]} '
                                                                      'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def map_presence(self) -> None:
        if self.cleaned_data['filter_map_id']:
            if not self._map:
                self.add_error('filter_map_id', ObjectDoesNotExist('Map id='
                                                                      f'{self.cleaned_data["filter_map_id"]} '
                                                                      'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def access_owner_or_superuser(self) -> None:
        if self._scheme and self._list_acc:
            if (self._scheme.creator != self.cleaned_data['current_user']
                    and not self.cleaned_data['current_user'].is_superuser):
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._scheme.pk} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
