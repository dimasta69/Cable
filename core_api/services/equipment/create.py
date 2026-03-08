from django import forms
from django.core.exceptions import ObjectDoesNotExist
from functools import lru_cache
from rest_framework import status

from core_api.utils.access_checker import scope_for_scheme
from core_api.utils.scheme_access import ResourceAccessMixin
from models_app.models import Scheme, Equipment, EquipmentTemplate, User
from utils.services import ServiceWithResult
from utils.fields import ModelField


class CreateEquipmentService(ResourceAccessMixin, ServiceWithResult):
    equipment_template_id = forms.IntegerField(required=True)
    scheme_id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ["equipment_template_presence", "scheme_presence", "access_presence"]

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

    def equipment_template_presence(self) -> None:
        if not self._equipment_template:
            self.add_error('equipment_template_id', ObjectDoesNotExist('Equipment template id='
                                                                       f'{self.cleaned_data["equipment_template_id"]}'
                                                                       ' not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def scheme_presence(self) -> None:
        if not self._scheme:
            self.add_error('scheme_id', ObjectDoesNotExist(
                f'Scheme id={self.cleaned_data["scheme_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
