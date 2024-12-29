from django import forms
from django.core.exceptions import ObjectDoesNotExist
from functools import lru_cache

from rest_framework import status

from models_app.models import Scheme
from utils.services import ServiceWithResult
from models_app.models import Equipment
from models_app.models import EquipmentTemplate


class CreateEquipmentService(ServiceWithResult):
    equipment_template_id = forms.IntegerField(required=True)
    scheme_id = forms.IntegerField(required=True)

    custom_validations = ["equipment_template_presence", "scheme_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_equipment
        return self

    @property
    def _create_equipment(self) -> Equipment:
        return Equipment.objects.create(template=self._equipment_template, scheme=self._scheme)

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
            return Scheme.objects.get(id=self.cleaned_data['scheme_id'])
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
            self.add_error('filter_scheme_id', ObjectDoesNotExist(
                f'Server rack id={self.cleaned_data["scheme_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
