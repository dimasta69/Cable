from django import forms
from functools import lru_cache
from rest_framework import status
from rest_framework.exceptions import NotFound

from core_api.utils.access_checker import scope_for_vlan
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Vlan, User


class UpdateVlanService(ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    id_name = forms.IntegerField(required=False)
    name = forms.CharField(required=False)
    current_user = ModelField(User)

    custom_validations = ['vlan_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_vlan
        return self

    @property
    def _update_vlan(self) -> Vlan:
        vlan = self._vlan
        if self.cleaned_data.get('name'):
            vlan.name = self.cleaned_data['name']
        if self.cleaned_data.get('id_name'):
            vlan.id_name = self.cleaned_data['id_name']
        vlan.save()
        return vlan

    def get_access_scope(self):
        return scope_for_vlan(self._vlan)

    @property
    @lru_cache()
    def _vlan(self) -> Vlan | None:
        try:
            return Vlan.objects.select_related('segment', 'segment__scheme').get(id=self.cleaned_data["id"])
        except Vlan.DoesNotExist:
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
