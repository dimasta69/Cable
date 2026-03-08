from django import forms
from functools import lru_cache
from rest_framework import status

from core_api.utils.access_checker import scope_for_map
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import EquipmentScheme, User


class UpdateEquipmentService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    coord_x = forms.IntegerField(required=False)
    coord_y = forms.IntegerField(required=False)
    current_user = ModelField(User)

    custom_validations = ['run_presence_checks', 'access_presence']
    presence_checks = [("_equipment", "id", "Equipment map")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_equipment
        return self

    @property
    def _update_equipment(self) -> EquipmentScheme:
        equipment = self._equipment
        if self.cleaned_data.get('coord_x') is not None:
            equipment.coord_x = self.cleaned_data['coord_x']
        if self.cleaned_data.get('coord_y') is not None:
            equipment.coord_y = self.cleaned_data['coord_y']
        equipment.save()
        return equipment

    def get_access_scope(self):
        return scope_for_map(self._equipment.schemes) if self._equipment else None

    @property
    @lru_cache()
    def _equipment(self) -> EquipmentScheme | None:
        try:
            return EquipmentScheme.objects.select_related(
                'schemes', 'schemes__scheme'
            ).get(id=self.cleaned_data['id'])
        except EquipmentScheme.DoesNotExist:
            return None
