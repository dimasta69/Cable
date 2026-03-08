from functools import lru_cache
from django import forms
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from rest_framework import status
from typing import List

from core_api.utils.access_checker import AccessChecker, scope_for_building
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from cabel.settings import REST_FRAMEWORK
from models_app.models import User, Room, Building
from utils.fields import ModelField
from utils.services import ServiceWithResult


class RoomListService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    current_user = ModelField(User)
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    order_by = forms.CharField(required=False)
    filter_building_id = forms.IntegerField(required=True)
    filter_is_server_room = forms.BooleanField(required=False)
    filter_floor = forms.IntegerField(required=False)
    search_filter = forms.CharField(required=False)

    access_required_roles = AccessChecker.ROLES_READ
    custom_validations = ['run_presence_checks', 'order_presence', 'access_presence']
    presence_checks = [("_building", "filter_building_id", "Building")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._room_pagination
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _room_pagination(self) -> Paginator:
        try:
            return (Paginator(self._room_filter_list, per_page=(self.cleaned_data['per_page'] or
                                                                REST_FRAMEWORK['PAGE_SIZE'])).
                    page(self.cleaned_data['page'] or 1))
        except EmptyPage:
            return (Paginator(self._room_filter_list, per_page=(self.cleaned_data['per_page'] or
                                                                REST_FRAMEWORK['PAGE_SIZE'])).page(1))

    @property
    def _room_filter_list(self) -> List[Room]:
        room_list = self._room_list
        if self.cleaned_data['filter_is_server_room']:
            room_list = room_list.filter(is_server_room=self.cleaned_data['filter_is_server_room'])
        if self.cleaned_data['filter_floor']:
            room_list = room_list.filter(floor=self.cleaned_data["filter_floor"])
        if self.cleaned_data['search_filter']:
            room_list = room_list.filter(
                Q(number__icontains=self.cleaned_data['search_filter']))
        if self.cleaned_data['order_by']:
            room_list = room_list.order_by(self.cleaned_data['order_by'])
        return room_list

    @property
    def _room_list(self) -> List[Room]:
        try:
            return Room.objects.filter(building=self._building)
        except Room.DoesNotExist:
            return Room.objects.none()

    def get_access_scope(self):
        return scope_for_building(self._building)

    @property
    @lru_cache()
    def _building(self) -> Building | None:
        try:
            return Building.objects.select_related("scheme").get(id=self.cleaned_data['filter_building_id'])
        except Building.DoesNotExist:
            return None

    def order_presence(self) -> None:
        if self.cleaned_data['order_by']:
            if not self.cleaned_data['order_by'] in ['number', '-number']:
                self.add_error('order', ObjectDoesNotExist(f'Order {self.cleaned_data["order_by"]} is not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

