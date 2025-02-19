from functools import lru_cache
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from rest_framework import status
from typing import List

from rest_framework.exceptions import PermissionDenied

from cabel.settings import REST_FRAMEWORK
from utils.errors import NotFound
from utils.fields import ListIntegerField, ModelField
from utils.services import ServiceWithResult
from models_app.models import (
    Scheme, Room, EquipmentTemplateType, EquipmentScheme, Equipment, Manufacturer, ServerRack, Access, User, Vlan,
    Segment, VlanDevice
)


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
    filter_segment_id = forms.IntegerField(required=False)
    filter_vlan_list_id = ListIntegerField(required=False)
    map_id = forms.IntegerField(required=False)
    current_user = ModelField(User)

    custom_validations = [
        'order_presence',
        'manufacturer_presence',
        'server_rack_presence',
        'scheme_presence',
        'room_presence',
        'type_presence',
        'access_presence',
        'segment_presence',
        'vlan_presence',
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._equipment_pagination
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _equipment_pagination(self) -> Paginator:
        try:
            return (Paginator(self._equipment_filter_list, per_page=(self.cleaned_data['per_page'] or
                                                                     REST_FRAMEWORK['PAGE_SIZE'])).
                    page(self.cleaned_data['page'] or 1))
        except EmptyPage:
            return (Paginator(self._equipment_filter_list, per_page=(self.cleaned_data['per_page'] or
                                                                     REST_FRAMEWORK['PAGE_SIZE'])).page(1))

    @property
    def _equipment_filter_list(self) -> List[Equipment]:
        equipment_content_type = ContentType.objects.get_for_model(Equipment)
        equipment_list = self._equipment_list.exclude(id__in=self._equipment_scheme_id)
        if self.cleaned_data['filter_segment_id']:
            equipment_list = equipment_list.filter(
                id__in=Vlan.objects.filter(
                    segment=self._segment, device__device_type=equipment_content_type
                ).values_list("device__device_id", flat=True)
            )
        if self.cleaned_data['filter_vlan_list_id']:
            equipment_list = equipment_list.filter(
                id__in=self._vlan.filter(
                    device__device_type=equipment_content_type
                ).values_list("device__device_id", flat=True)
            )
        if self.cleaned_data['filter_manufacturer_id']:
            equipment_list = equipment_list.filter(template__manufacturer=self._manufacturer)
        if self.cleaned_data['filter_type_id']:
            equipment_list = equipment_list.filter(template__type=self._type)
        if self.cleaned_data['filter_scheme_id']:
            equipment_list = equipment_list.filter(scheme=self._scheme).distinct()
        if self.cleaned_data['filter_server_rack_id']:
            equipment_list = equipment_list.filter(unit__server_rack=self._server_rack).distinct()
        if self.cleaned_data['filter_room_id']:
            equipment_list = equipment_list.filter(room=self._room)
        if self.cleaned_data['search_filter']:
            equipment_list = equipment_list.filter(
                Q(template__model__icontains=self.cleaned_data['search_filter']) |
                Q(template__manufacturer__name__icontains=self.cleaned_data['search_filter']) |
                Q(id__in=VlanDevice.objects.filter(vlan__segment__scheme=self._scheme).filter(
                    Q(ip__icontains=self.cleaned_data['search_filter'])
                    ).values_list('device_id', flat=True))
            )
        if self.cleaned_data['order_by']:
            equipment_list = equipment_list.order_by(self.cleaned_data['order_by'])
        return equipment_list

    @property
    def _equipment_list(self) -> List[Equipment]:
        try:
            return Equipment.objects.all().select_related(
                'template',
                'template__manufacturer',
            ).prefetch_related(
                'connections',
            )
        except Equipment.DoesNotExist:
            return Equipment.objects.none()

    @property
    def _equipment_scheme_id(self) -> List[EquipmentScheme]:
        try:
            return EquipmentScheme.objects.filter(schemes__id=self.cleaned_data.get("map_id")).values_list('id')
        except EquipmentScheme.DoesNotExist:
            return EquipmentScheme.objects.none()

    @property
    @lru_cache()
    def _manufacturer(self) -> Manufacturer | None:
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['filter_manufacturer_id'])
        except Manufacturer.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _scheme(self):
        try:
            return Scheme.objects.get(id=self.cleaned_data['filter_scheme_id'])
        except Scheme.DoesNotExist:
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
    def _room(self) -> Room | None:
        try:
            return Room.objects.get(id=self.cleaned_data['filter_room_id'])
        except Room.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _type(self) -> EquipmentTemplateType | None:
        try:
            return EquipmentTemplateType.objects.get(id=self.cleaned_data['filter_type_id'])
        except EquipmentTemplateType.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        try:
            return Access.objects.filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator'],
                object_type=scheme_content_type,
                object_id=self._scheme.id,
            )
        except Access.DoesNotExist:
            return None

    @property
    @lru_cache
    def _segment(self) -> Segment | None:
        try:
            return Segment.objects.get(id=self.cleaned_data["filter_scheme_id"])
        except Segment.DoesNotExist:
            return None

    @property
    @lru_cache
    def _vlan(self) -> List[Vlan]:
        try:
            return Vlan.objects.filter(id__in=self.cleaned_data["filter_vlan_list_id"], segment=self._segment)
        except Vlan.DoesNotExist:
            return Vlan.objects.none()

    def order_presence(self) -> None:
        if self.cleaned_data['order_by']:
            if not self.cleaned_data['order_by'] in ['template__power', '-template__power', 'template__number_of_units',
                                                     '-template__number_of_units', 'template__count_port',
                                                     '-template__count_port', 'template__model', '-template__model',
                                                     'free_ports', '-free_ports']:
                self.add_error('order', ObjectDoesNotExist(f'Order {self.cleaned_data["order_by"]} is not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def manufacturer_presence(self) -> None:
        if self.cleaned_data['filter_manufacturer_id']:
            if not self._manufacturer:
                self.add_error('filter_manufacturer_id', ObjectDoesNotExist(
                    f'Manufacturer id={self.cleaned_data["filter_manufacturer_id"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def server_rack_presence(self) -> None:
        if self.cleaned_data['filter_server_rack_id']:
            if not self._server_rack:
                self.add_error('filter_server_rack_id', ObjectDoesNotExist(
                    f'Server rack id={self.cleaned_data["filter_server_rack_id"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def scheme_presence(self) -> None:
        if self.cleaned_data['filter_scheme_id']:
            if not self._scheme:
                self.add_error('filter_scheme_id', ObjectDoesNotExist(
                    f'Server rack id={self.cleaned_data["filter_scheme_id"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def room_presence(self) -> None:
        if self.cleaned_data["filter_room_id"] and not self._room:
            self.add_error('filter_room_id', ObjectDoesNotExist(f"Room id ={self.cleaned_data['filter_room_id']} "
                                                                "not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def type_presence(self) -> None:
        if self.cleaned_data['filter_type_id'] and self._type is None:
            self.add_error('filter_type', ObjectDoesNotExist('Type id='
                                                             f'{self.cleaned_data["filter_type_id"]} '
                                                             f'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if self._scheme:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN

    def segment_presence(self) -> None:
        if self.cleaned_data['filter_segment_id'] and not self._segment:
            self.add_error(
                "filter_segment_id",
                NotFound(
                    f"Segment id={self.cleaned_data['filter_segment_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def vlan_presence(self) -> None:
        if self.cleaned_data["filter_vlan_list_id"]:
            if len(self.cleaned_data['filter_vlan_list_id']) != len(self._vlan) or not self._segment:
                self.add_error(
                    "filter_vlan_list_id",
                    NotFound(
                        f"Vlan id={self.cleaned_data['filter_vlan_list_id']} not found"
                    )
                )
                self.response_status = status.HTTP_404_NOT_FOUND
