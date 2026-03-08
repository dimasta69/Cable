from django import forms
from functools import lru_cache
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from rest_framework import status
from typing import List

from core_api.utils.access_checker import AccessChecker, scope_for_room
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from models_app.models import User, Room, ServerRack
from utils.fields import ModelField
from utils.services import ServiceWithResult
from cabel.settings import REST_FRAMEWORK


class ServerRackListService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    filter_room_id = forms.IntegerField(required=True)
    order_by = forms.CharField(required=False)
    search_filter = forms.CharField(required=False)
    current_user = ModelField(User)

    access_required_roles = AccessChecker.ROLES_READ
    custom_validations = ['run_presence_checks', 'order_presence', 'access_presence']
    presence_checks = [("_room", "filter_room_id", "Room")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.server_rack_pagination
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def server_rack_pagination(self):
        try:
            return (Paginator(self._filter_server_rack_list, per_page=(self.cleaned_data['per_page'] or
                                                                       REST_FRAMEWORK['PAGE_SIZE'])).
                    page(self.cleaned_data['page'] or 1))
        except EmptyPage:
            return (Paginator(self._filter_server_rack_list, per_page=(self.cleaned_data['per_page'] or
                                                                       REST_FRAMEWORK['PAGE_SIZE'])).page(1))

    @property
    def _filter_server_rack_list(self) -> List[ServerRack]:
        server_rack_list = self._server_rack_list
        if self.cleaned_data['search_filter']:
            server_rack_list = server_rack_list.filter(
                Q(title__icontains=self.cleaned_data['search_filter'])
            )
        return server_rack_list

    @property
    def _server_rack_list(self) -> List[ServerRack]:
        try:
            return ServerRack.objects.filter(room=self._room)
        except ServerRack.DoesNotExist:
            return ServerRack.objects.none()

    def get_access_scope(self):
        return scope_for_room(self._room)

    @property
    @lru_cache()
    def _room(self) -> Room | None:
        try:
            return Room.objects.select_related('building', 'building__scheme').get(
                id=self.cleaned_data['filter_room_id']
            )
        except Room.DoesNotExist:
            return None

    def order_presence(self) -> None:
        if self.cleaned_data['order_by']:
            if not self.cleaned_data['order_by'] in ['title', '-title', 'max_power', '-max_power', 'free_power',
                                                     '-free_power', 'free_units', '-free_units']:
                self.add_error('order', ObjectDoesNotExist(f'Order {self.cleaned_data["order_by"]} is not found'))
                self.response_status = status.HTTP_404_NOT_FOUND
