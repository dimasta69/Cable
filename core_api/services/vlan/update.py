from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from functools import lru_cache
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied

from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Vlan, User, Segment, Access, Scheme


class UpdateVlanService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    name = forms.CharField(required=False)
    current_user = ModelField(User)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)
    segment_content_type = ContentType.objects.get_for_model(Segment)
    vlan_content_type = ContentType.objects.get_for_model(Vlan)


    custom_validations = ['vlan_presence', 'access_presence', ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_vlan
        return self

    @property
    def _update_vlan(self) -> Vlan:
        vlan = self._vlan
        if self.cleaned_data['name']:
            vlan.name = self.cleaned_data['name']
        return vlan

    @property
    @lru_cache()
    def _vlan(self) -> Vlan | None:
        try:
            return Vlan.objects.get(id=self.cleaned_data["id"])
        except Vlan.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        try:
            return Access.objects.filter(
                Q(
                    object_type=self.scheme_content_type,
                    object_id=self._vlan.segment.scheme.pk,
                ) |
                Q(
                    object_type=self.segment_content_type,
                    object_id=self._vlan.segment.pk,
                ) |
                Q(
                    object_type=self.vlan_content_type,
                    object_id=self._vlan.pk,
                )
            ).filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator']
            )
        except Access.DoesNotExist:
            return None

    def vlan_presence(self) -> None:
        if not self._vlan:
            self.add_error(
                "id",
                NotFound(
                    f"Vlan with id={self.cleaned_data['id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if not self._access:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schem id = '
                                                                f'{self._vlan.pk} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
