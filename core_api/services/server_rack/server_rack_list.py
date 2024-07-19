from django import forms
from functools import lru_cache
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status

from models_app.models import User, Access
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models.room import Room
from models_app.models.server_rack import ServerRack


class ServerRackListService(ServiceWithResult):
    filter_room_id = forms.IntegerField(required=True)
    order_by = forms.CharField(required=False)
    search_filter = forms.CharField(required=False)
    current_user = ModelField(User)

    custom_validations = ['room_presence', 'order_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.filter_server_rack_list
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def filter_server_rack_list(self):
        server_rack_list = self.server_rack_list
        if self.cleaned_data['search_filter']:
            server_rack_list = server_rack_list.filter(
                Q(title__icontains=self.cleaned_data['search_filter'])
            )
        return server_rack_list

    @property
    def server_rack_list(self):
        try:
            return ServerRack.objects.filter(room=self.room)
        except ServerRack.DoesNotExist:
            return ServerRack.objects.none()

    @property
    @lru_cache()
    def room(self):
        try:
            return Room.objects.get(id=self.cleaned_data['filter_room_id'])
        except Room.DoesNotExist:
            return None

    @property
    def access(self):
        try:
            return Access.objects.get(user=self.cleaned_data['current_user'], scheme=self.room.building.scheme)
        except Access.DoesNotExist:
            return None

    def room_presence(self):
        if self.cleaned_data['filter_room_id']:
            if not self.room:
                self.add_error('filter_room_id', ObjectDoesNotExist('Room id='
                                                                    f'{self.cleaned_data["filter_room_id"]} '
                                                                    'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def order_presence(self):
        if self.cleaned_data['order_by']:
            if not self.cleaned_data['order_by'] in ['title', '-title', 'max_power', '-max_power', 'free_power',
                                                     '-free_power', 'free_units', '-free_units']:
                self.add_error('order', ObjectDoesNotExist(f'Order {self.cleaned_data["order_by"]} is not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self):
        if self.room:
            if not self.access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.room.building.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
