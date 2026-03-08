from django import forms
from functools import lru_cache

from rest_framework import status

from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import SchemeAccessMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Equipment, User


class EquipmentService(PresenceChecksMixin, SchemeAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['run_presence_checks', 'access_presence']
    presence_checks = [("_equipment", "id", "Equipment")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._equipment
            self.response_status = status.HTTP_200_OK
        return self

    def _get_scheme_id_for_access(self):
        if self._equipment and self._equipment.scheme_id:
            return self._equipment.scheme_id
        return None

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.select_related("scheme").get(id=self.cleaned_data['id'])
        except Equipment.DoesNotExist:
            return None
