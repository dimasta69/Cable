from django import forms
from functools import lru_cache
from rest_framework import status

from core_api.utils.access_checker import scope_for_scheme
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from models_app.models import Scheme, Equipment, EquipmentTemplate, User
from utils.services import ServiceWithResult
from utils.fields import ModelField


class CreateEquipmentService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    equipment_template_id = forms.IntegerField(required=True)
    scheme_id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ["run_presence_checks", "access_presence"]
    presence_checks = [
        ("_equipment_template", "equipment_template_id", "Equipment template"),
        ("_scheme", "scheme_id", "Scheme"),
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_equipment
        return self

    @property
    def _create_equipment(self) -> Equipment:
        return Equipment.objects.create(template=self._equipment_template, scheme=self._scheme)

    def get_access_scope(self):
        return scope_for_scheme(self._scheme)

    @property
    @lru_cache()
    def _equipment_template(self) -> Equipment | None:
        try:
            return EquipmentTemplate.objects.get(id=self.cleaned_data['equipment_template_id'])
        except EquipmentTemplate.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.prefetch_related(
                "buildings", "buildings__rooms", "buildings__rooms__server_racks"
            ).get(id=self.cleaned_data['scheme_id'])
        except Scheme.DoesNotExist:
            return None
