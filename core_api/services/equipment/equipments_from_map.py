from functools import lru_cache
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from rest_framework import status
from typing import List

from core_api.utils.access_checker import AccessChecker, scope_for_scheme
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from cabel.settings import REST_FRAMEWORK
from utils.errors import NotFound
from utils.fields import ListIntegerField, ModelField
from utils.services import ServiceWithResult
from models_app.models import (
    Scheme, Room, EquipmentTemplateType, EquipmentScheme, Equipment, Manufacturer, ServerRack, User, Vlan,
    Segment, VlanDevice
)


class EquipmentsFromMapListService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
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

    access_required_roles = AccessChecker.ROLES_READ
    custom_validations = [
        'run_presence_checks',
        'order_presence',
        'access_presence',
        'vlan_presence',
    ]
    presence_checks = [
        ("_scheme", "filter_scheme_id", "Scheme"),
        ("_manufacturer", "filter_manufacturer_id", "Manufacturer", True),
        ("_server_rack", "filter_server_rack_id", "Server rack", True),
        ("_room", "filter_room_id", "Room", True),
        ("_type", "filter_type_id", "Type", True),
        ("_segment", "filter_segment_id", "Segment", True),
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

    def get_access_scope(self):
        return scope_for_scheme(self._scheme)

    @property
    @lru_cache()
    def _segment(self) -> Segment | None:
        try:
            return Segment.objects.get(id=self.cleaned_data["filter_segment_id"])
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
