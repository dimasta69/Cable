from functools import lru_cache
from django import forms
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from rest_framework import status

from cabel.settings import REST_FRAMEWORK
from models_app.models import Access, User
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Room
from models_app.models import Building


class RoomListService(ServiceWithResult):
    current_user = ModelField(User)
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    order_by = forms.CharField(required=False)
    filter_building_id = forms.IntegerField(required=True)
    filter_is_server_room = forms.BooleanField(required=False)
    search_filter = forms.CharField(required=False)

    custom_validations = ['building_presence', 'order_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.room_pagination
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def room_pagination(self):
        try:
            return (Paginator(self.room_filter_list, per_page=(self.cleaned_data['per_page'] or
                                                               REST_FRAMEWORK['PAGE_SIZE'])).
                    page(self.cleaned_data['page'] or 1))
        except EmptyPage:
            return (Paginator(self.room_filter_list, per_page=(self.cleaned_data['per_page'] or
                                                               REST_FRAMEWORK['PAGE_SIZE'])).page(1))

    @property
    def room_filter_list(self):
        room_list = self.room_list
        if self.cleaned_data['filter_is_server_room']:
            room_list = room_list.filter(is_server_room=self.cleaned_data['filter_is_server_room'])
        if self.cleaned_data['search_filter']:
            room_list = room_list.filter(
                Q(number__icontains=self.cleaned_data['search_filter']))
        if self.cleaned_data['order_by']:
            room_list = room_list.order_by(self.cleaned_data['order_by'])
        return room_list

    @property
    def room_list(self):
        try:
            return Room.objects.filter(building=self.building)
        except Room.DoesNotExist:
            return Room.objects.none()

    @property
    @lru_cache()
    def building(self):
        try:
            return Building.objects.get(id=self.cleaned_data['filter_building_id'])
        except Building.DoesNotExist:
            return None

    @property
    def access(self):
        try:
            return Access.objects.get(user=self.cleaned_data['current_user'], scheme=self.building.scheme)
        except Access.DoesNotExist:
            return None

    def order_presence(self):
        if self.cleaned_data['order_by']:
            if not self.cleaned_data['order_by'] in ['number', '-number']:
                self.add_error('order', ObjectDoesNotExist(f'Order {self.cleaned_data["order_by"]} is not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def building_presence(self):
        if self.cleaned_data['filter_building_id']:
            if not self.building:
                self.add_error('filter_building_id', ObjectDoesNotExist('Building id='
                                                                        f'{self.cleaned_data["filter_building_id"]} '
                                                                        'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self):
        if self.building:
            if not self.access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.building.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
