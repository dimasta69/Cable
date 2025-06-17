from django import forms
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from functools import lru_cache
from rest_framework import status

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models.equipment.equipment_template.models import EquipmentTemplate
from models_app.models import User


class DeleteEquipmentTemplateService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['equipment_template_presence', 'is_superuser']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.delete_equipment_template()
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    def delete_equipment_template(self) -> None:
        self._equipment_template.delete()

    @property
    @lru_cache()
    def _equipment_template(self) -> EquipmentTemplate | None:
        try:
            return EquipmentTemplate.objects.get(id=self.cleaned_data['id'])
        except EquipmentTemplate.DoesNotExist:
            return None

    def equipment_template_presence(self) -> None:
        if not self._equipment_template:
            self.add_error('id', ObjectDoesNotExist(f'Equipment template id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied(
                    "User is not superuser"
                )
            )
