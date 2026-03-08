from functools import lru_cache
from typing import List

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from core_api.utils.access_checker import (
    AccessChecker,
    scope_for_segment,
)
from core_api.utils.presence import PresenceChecksMixin
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Vlan, Segment, User, Access, Scheme


class VlanListService(PresenceChecksMixin, ServiceWithResult):
    current_user = ModelField(User)
    segment_id = forms.IntegerField(required=True)
    search_field = forms.CharField(required=False)

    custom_validations = ['run_presence_checks', 'access_presence']
    presence_checks = [("_segment", "segment_id", "Segment")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._vlan_list
        return self

    @property
    def _vlan_list(self) -> List[Vlan]:
        vlan_list = None
        if self._has_scheme_or_segment_access:
            vlan_list = self._vlan_list_access_segment
        elif self._access_vlan:
            vlan_list = self._vlan_list_access_vlan
        if vlan_list is not None and self.cleaned_data.get('search_field'):
            vlan_list = vlan_list.filter(
                Q(name__icontains=self.cleaned_data['search_field']),
            )
        return vlan_list or Vlan.objects.none()

    @property
    def _vlan_list_access_segment(self) -> List[Vlan]:
        try:
            return Vlan.objects.filter(segment=self._segment)
        except Vlan.DoesNotExist:
            return Vlan.objects.none()

    @property
    def _vlan_list_access_vlan(self) -> List[Vlan]:
        try:
            return Vlan.objects.filter(
                segment=self._segment,
                id__in=self._access_vlan.values_list("object_id", flat=True),
            )
        except Vlan.DoesNotExist:
            return Vlan.objects.none()

    @property
    @lru_cache()
    def _segment(self) -> Segment | None:
        try:
            return Segment.objects.select_related('scheme').get(id=self.cleaned_data["segment_id"])
        except Segment.DoesNotExist:
            return None

    @property
    def _has_scheme_or_segment_access(self) -> bool:
        scope = scope_for_segment(self._segment)
        return AccessChecker.has_permission(
            self.cleaned_data['current_user'],
            AccessChecker.ROLES_READ,
            scope,
        ) if scope else False

    @property
    def _access_vlan(self):
        from models_app.models import Vlan as VlanModel
        vlan_content_type = ContentType.objects.get_for_model(VlanModel)
        if not self._segment:
            return Access.objects.none()
        return Access.objects.filter(
            user=self.cleaned_data['current_user'],
            object_type=vlan_content_type,
            object_id__in=self._segment.vlans.values_list('id', flat=True),
        )

    def access_presence(self) -> None:
        if not self._segment:
            return
        user = self.cleaned_data['current_user']
        if user and getattr(user, 'is_superuser', False):
            return
        scope = scope_for_segment(self._segment)
        if AccessChecker.has_permission(user, AccessChecker.ROLES_READ, scope):
            return
        if AccessChecker.has_permission_to_any_vlan_in_segment(
            user, self._segment, AccessChecker.ROLES_READ
        ):
            return
        self.add_error(
            'current_user',
            PermissionDenied(
                f'Access to the scheme id = {self._segment.scheme_id} is not granted'
            ),
        )
        self.response_status = status.HTTP_403_FORBIDDEN
