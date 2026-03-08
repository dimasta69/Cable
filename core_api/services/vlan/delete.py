from django import forms
from functools import lru_cache
from rest_framework import status

from core_api.utils.access_checker import scope_for_vlan
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Vlan, User


class DeleteVlanService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['run_presence_checks', 'access_presence']
    presence_checks = [("_vlan", "id", "Vlan")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._delete_vlan()
        return self

    def _delete_vlan(self) -> None:
        self._vlan.delete()

    def get_access_scope(self):
        return scope_for_vlan(self._vlan)

    @property
    @lru_cache()
    def _vlan(self) -> Vlan | None:
        try:
            return Vlan.objects.select_related('segment', 'segment__scheme').get(id=self.cleaned_data["id"])
        except Vlan.DoesNotExist:
            return None
