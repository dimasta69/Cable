from django import forms
from functools import lru_cache
from rest_framework import status

from core_api.utils.access_checker import scope_for_map
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import User, EquipmentScheme


class DeleteEquipmentSchemeService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['run_presence_checks', 'access_presence']
    presence_checks = [("_equipment", "id", "Equipment map")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._delete_equipment()
        return self

    def _delete_equipment(self) -> None:
        self._equipment.delete()

    def get_access_scope(self):
        if self._equipment and getattr(self._equipment, 'schemes', None):
            return scope_for_map(self._equipment.schemes)
        return None

    @property
    @lru_cache()
    def _equipment(self) -> EquipmentScheme | None:
        try:
            return EquipmentScheme.objects.select_related(
                "schemes", "schemes__scheme"
            ).get(id=self.cleaned_data['id'])
        except EquipmentScheme.DoesNotExist:
            return None
