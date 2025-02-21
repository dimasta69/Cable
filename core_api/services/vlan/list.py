from functools import lru_cache
from typing import List

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from utils.errors import NotFound
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Vlan, Segment, User, Access, Scheme


class VlanListService(ServiceWithResult):
    current_user = ModelField(User)
    segment_id = forms.IntegerField(required=True)
    search_field = forms.CharField(required=False)

    custom_validations = ['segment_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._vlan_list
        return self

    @property
    def _vlan_list(self) -> List[Vlan]:
        vlan_list = None
        breakpoint()
        if self._access:
            vlan_list = self._vlan_list_access_segment
        elif self._access_vlan:
            vlan_list = self._vlan_list_access_vlan
        if self.cleaned_data['search_field']:
            vlan_list = vlan_list.filter(
                Q(name__icontains=self.cleaned_data['search_field']),
            )
        return vlan_list

    @property
    def _vlan_list_access_segment(self) -> List[Vlan]:
        try:
            return Vlan.objects.filter(segment=self._segment)
        except Vlan.DoesNotExist:
            return Vlan.objects.none()

    @property
    def _vlan_list_access_vlan(self) -> List[Vlan]:
        try:
            return Vlan.objects.filter(segment=self._segment, id__in=self._access_vlan.values("object_id"))
        except Vlan.DoesNotExist:
            return Vlan.objects.none()

    @property
    @lru_cache()
    def _segment(self) -> Segment | None:
        try:
            return Segment.objects.get(id=self.cleaned_data["segment_id"])
        except Segment.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        segment_content_type = ContentType.objects.get_for_model(Segment)
        try:
            return Access.objects.filter(
                Q(
                    object_type=scheme_content_type,
                    object_id=self._segment.scheme.id,
                ) |
                Q(
                    object_type=segment_content_type,
                    object_id=self._segment.id,
                )
            ).filter(
                user=self.cleaned_data['current_user'],
            )
        except Access.DoesNotExist:
            return None

    @property
    def _access_vlan(self) -> Access | None:
        vlan_content_type = ContentType.objects.get_for_model(Vlan)
        try:
            return Access.objects.filter(
                Q(
                    object_type=vlan_content_type,
                    object_id__in=self._segment.vlans.values_list('id', flat=True),
                ),
            ).filter(
                user=self.cleaned_data['current_user'],
            )
        except Access.DoesNotExist:
            return None

    def segment_presence(self) -> None:
        if self.cleaned_data['segment_id'] and not self._segment:
            self.add_error(
                "segment_id",
                NotFound(
                    f"Segment with id={self.cleaned_data['segment_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if self._segment:
            if not self._access and not self._access_vlan:
                if not self._access and not self.cleaned_data['current_user'].is_superuser:
                    self.add_error('current_user', PermissionDenied('Access to the scheme id = '
                                                                    f'{self._segment.id} is not granted'))
                    self.response_status = status.HTTP_403_FORBIDDEN
