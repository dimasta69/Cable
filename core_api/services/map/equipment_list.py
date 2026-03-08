from django import forms
from functools import lru_cache
from typing import List

from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.exceptions import NotFound

from core_api.utils.access_checker import AccessChecker, scope_for_map
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.fields import ModelField, ListIntegerField
from utils.services import ServiceWithResult
from models_app.models import EquipmentScheme, SchemeMap, User, Vlan, Segment, Equipment


class EquipmentListService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    filter_segment_id = forms.IntegerField(required=False)
    filter_vlan_list_id = ListIntegerField(required=False)
    current_user = ModelField(User)

    access_required_roles = AccessChecker.ROLES_READ
    custom_validations = [
        'run_presence_checks',
        'access_presence',
        'vlan_presence',
    ]
    presence_checks = [
        ("_map", "id", "Map"),
        ("_segment", "filter_segment_id", "Segment", True),
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._equipment_filter
        return self

    @property
    def _equipment_filter(self) -> List[EquipmentScheme]:
        equipments = self._equipment_list
        equipment_content_type = ContentType.objects.get_for_model(Equipment)
        if self.cleaned_data.get('filter_segment_id'):
            equipments = equipments.filter(
                equipment_id__in=Vlan.objects.filter(
                    segment=self._segment, device__device_type=equipment_content_type
                ).values_list("device__device_id", flat=True)
            )
        if self.cleaned_data.get('filter_vlan_list_id'):
            equipments = equipments.filter(
                equipment_id__in=self._vlan.filter(
                    device__device_type=equipment_content_type
                ).values_list("device__device_id", flat=True)
            )
        return equipments

    @property
    def _equipment_list(self) -> List[EquipmentScheme]:
        try:
            return EquipmentScheme.objects.filter(
                schemes=self._map
            ).select_related("equipment__scheme").prefetch_related(
                "equipment__scheme__segments",
            )
        except EquipmentScheme.DoesNotExist:
            return EquipmentScheme.objects.none()

    def get_access_scope(self):
        return scope_for_map(self._map)

    @property
    @lru_cache()
    def _map(self) -> SchemeMap | None:
        try:
            return SchemeMap.objects.select_related('scheme').get(id=self.cleaned_data['id'])
        except SchemeMap.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _segment(self) -> Segment | None:
        try:
            return Segment.objects.get(id=self.cleaned_data["filter_segment_id"])
        except Segment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _vlan(self) -> List[Vlan]:
        try:
            return Vlan.objects.filter(
                id__in=self.cleaned_data.get("filter_vlan_list_id") or [],
                segment=self._segment
            )
        except Vlan.DoesNotExist:
            return Vlan.objects.none()

    def vlan_presence(self) -> None:
        if self.cleaned_data.get("filter_vlan_list_id"):
            if len(self.cleaned_data['filter_vlan_list_id']) != len(self._vlan) or not self._segment:
                self.add_error(
                    "filter_vlan_list_id",
                    NotFound(
                        f"Vlan id={self.cleaned_data['filter_vlan_list_id']} not found"
                    )
                )
                self.response_status = status.HTTP_404_NOT_FOUND
