from django import forms
from django.core.exceptions import PermissionDenied
from functools import lru_cache
from rest_framework import status

from core_api.utils.presence import PresenceChecksMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models.equipment.equipment_template.models import EquipmentTemplate
from models_app.models import User


class DeleteEquipmentTemplateService(PresenceChecksMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['run_presence_checks', 'is_superuser']
    presence_checks = [("_equipment_template", "id", "Equipment template")]

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

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied(
                    "User is not superuser"
                )
            )
