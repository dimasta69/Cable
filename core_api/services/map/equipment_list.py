from django import forms
from functools import lru_cache

from typing import List

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied

from utils.fields import ModelField, ListIntegerField
from utils.services import ServiceWithResult
from models_app.models import EquipmentScheme, SchemeMap, Access, User, Scheme, Vlan, Segment, Equipment


class EquipmentListService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    filter_segment_id = forms.IntegerField(required=False)
    filter_vlan_list_id = ListIntegerField(required=False)
    current_user = ModelField(User)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)
    equipment_content_type = ContentType.objects.get_for_model(Equipment)

    custom_validations = [
        'map_presence',
        'access_presence',
        'segment_presence',
        'vlan_presence',
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._equipment_list
        return self

    @property
    def _equipment_filter(self) -> List[EquipmentScheme]:
        equipments = self._equipment_list
        if self.cleaned_data['filter_segment_id']: 
            equipments = equipments.filter(equipment__scheme__segment__in=[self._segment])
        if self.cleaned_data['filter_vlan_list_id']:
            equipments = equipments.filter(
                equipment__in=self._vlan.filter(device_type=self.equipment_content_type).values("id")
            )

    @property
    def _equipment_list(self) -> List[EquipmentScheme]:
        try:
            return EquipmentScheme.objects.filter(
                schemes=self._map
            ).select_related("equipment__scheme").prefetch_related(
                "equipment__scheme__segment",
            )
        except EquipmentScheme.DoesNotExist:
            return EquipmentScheme.objects.none()

    @property
    @lru_cache()
    def _map(self) -> SchemeMap | None:
        try:
            return SchemeMap.objects.get(id=self.cleaned_data['id'])
        except SchemeMap.DoesNotExist:
            return None

    @property
    def _access(self):
        try:
            return Access.objects.filter(
                Q(
                    object_type=self.scheme_content_type,
                    object_id=self._map.scheme.pk,
                ),
            ).filter(
                user=self.cleaned_data['current_user'],
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
            return Vlan.objects.get(id__in=self.cleaned_data["filter_vlan_list_id"], segment=self._segment)
        except Vlan.DoesNotExist:
            return Vlan.objects.none()

    def map_presence(self) -> None:
        if not self._map:
            self.add_error(
                "id",
                NotFound(
                    f"Map id={self.cleaned_data['id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if self.cleaned_data['id']:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the map id = '
                                                                f'{self.cleaned_data["id"]} is not granted'))
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
            if len(self.cleaned_data['filter_vlan_list_id']) != self._vlans or not self._segment:
                self.add_error(
                    "filter_segment_id",
                    NotFound(
                        f"Segment id={self.cleaned_data['filter_segment_id']} not found"
                    )
                )
                self.response_status = status.HTTP_404_NOT_FOUND
