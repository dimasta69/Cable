from functools import lru_cache
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from rest_framework import status

from cabel.settings import REST_FRAMEWORK
from utils.services import ServiceWithResult
from models_app.models import Scheme, Room, EquipmentTemplateType
from models_app.models import Equipment
from models_app.models import Manufacturer
from models_app.models import ServerRack


class EquipmentsFromMapListService(ServiceWithResult):
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    order_by = forms.CharField(required=False)
    filter_manufacturer_id = forms.IntegerField(required=False)
    filter_type_id = forms.IntegerField(required=False)
    search_filter = forms.CharField(required=False)
    filter_scheme_id = forms.IntegerField(required=True)
    filter_room_id = forms.IntegerField(required=False)
    filter_server_rack_id = forms.IntegerField(required=False)

    custom_validations = ['order_presence', 'manufacturer_presence', 'server_rack_presence',
                          'scheme_presence', 'room_presence', 'type_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.equipment_pagination
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def equipment_pagination(self):
        try:
            return (Paginator(self.equipment_filter_list, per_page=(self.cleaned_data['per_page'] or
                                                                    REST_FRAMEWORK['PAGE_SIZE'])).
                    page(self.cleaned_data['page'] or 1))
        except EmptyPage:
            return (Paginator(self.equipment_filter_list, per_page=(self.cleaned_data['per_page'] or
                                                                    REST_FRAMEWORK['PAGE_SIZE'])).page(1))

    @property
    def equipment_filter_list(self):
        equipment_list = self.equipment_list
        if self.cleaned_data['filter_manufacturer_id']:
            equipment_list = equipment_list.filter(template__manufacturer=self._manufacturer)
        if self.cleaned_data['filter_type_id']:
            equipment_list = equipment_list.filter(template__type=self._type)
        if self.cleaned_data['filter_scheme_id']:
            equipment_list = equipment_list.filter(scheme=self.scheme).distinct()
        if self.cleaned_data['filter_server_rack_id']:
            equipment_list = equipment_list.filter(unit__server_rack=self.server_rack).distinct()
        if self.cleaned_data['filter_room_id']:
            equipment_list = equipment_list.filter(room=self._room)
        if self.cleaned_data['search_filter']:
            equipment_list = equipment_list.filter(
                Q(template__model__icontains=self.cleaned_data['search_filter']) |
                Q(template__manufacturer__name__icontains=self.cleaned_data['search_filter'])
            )
        if self.cleaned_data['order_by']:
            equipment_list = equipment_list.order_by(self.cleaned_data['order_by'])
        return equipment_list

    @property
    def equipment_list(self):
        try:
            return Equipment.objects.all().select_related('template', 'template__manufacturer')
        except Equipment.DoesNotExist:
            return Equipment.objects.none()

    @property
    @lru_cache()
    def _manufacturer(self):
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['filter_manufacturer_id'])
        except Manufacturer.DoesNotExist:
            return None

    @property
    @lru_cache()
    def scheme(self):
        try:
            return Scheme.objects.get(id=self.cleaned_data['filter_scheme_id'])
        except Scheme.DoesNotExist:
            return None

    @property
    @lru_cache()
    def server_rack(self):
        try:
            return ServerRack.objects.get(id=self.cleaned_data['filter_server_rack_id'])
        except ServerRack.DoesNotExist:
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
    def _type(self):
        try:
            return EquipmentTemplateType.objects.get(id=self.cleaned_data['filter_type_id'])
        except EquipmentTemplateType.DoesNotExist:
            return None

    def order_presence(self):
        if self.cleaned_data['order_by']:
            if not self.cleaned_data['order_by'] in ['template__power', '-template__power', 'template__number_of_units',
                                                     '-template__number_of_units', 'template__count_port',
                                                     '-template__count_port', 'template__model', '-template__model',
                                                     'free_ports', '-free_ports']:
                self.add_error('order', ObjectDoesNotExist(f'Order {self.cleaned_data["order_by"]} is not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def manufacturer_presence(self):
        if self.cleaned_data['filter_manufacturer_id']:
            if not self._manufacturer:
                self.add_error('filter_manufacturer_id', ObjectDoesNotExist(
                    'Manufacturer id={self.cleaned_data["filter_manufacturer_id"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def server_rack_presence(self):
        if self.cleaned_data['filter_server_rack_id']:
            if not self.server_rack:
                self.add_error('filter_server_rack_id', ObjectDoesNotExist(
                    f'Server rack id={self.cleaned_data["filter_server_rack_id"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def scheme_presence(self):
        if self.cleaned_data['filter_scheme_id']:
            if not self.scheme:
                self.add_error('filter_scheme_id', ObjectDoesNotExist(
                    f'Server rack id={self.cleaned_data["filter_scheme_id"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def room_presence(self) -> None:
        if self.cleaned_data["filter_room_id"] and not self._room:
            self.add_error('filter_room_id', ObjectDoesNotExist(f"Room id ={self.cleaned_data['filter_room_id']} "
                                                                "not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def type_presence(self):
        if self.cleaned_data['filter_type_id'] and self._type is None:
            self.add_error('filter_type', ObjectDoesNotExist('Type id='
                                                             f'{self.cleaned_data["filter_type_id"]} '
                                                             f'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
