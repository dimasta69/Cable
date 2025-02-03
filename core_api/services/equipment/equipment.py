from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from functools import lru_cache

from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Equipment, Access, Scheme, User


class EquipmentService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)

    custom_validations = ['equipment_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._equipment
            self.response_status = status.HTTP_200_OK
        return self

    @property
    @lru_cache()
    def _equipment(self) -> Equipment | None:
        try:
            return Equipment.objects.select_related("scheme").get(id=self.cleaned_data['id'])
        except Equipment.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        try:
            return Access.objects.filter(
                user=self.cleaned_data['current_user'],
                object_type=self.scheme_content_type,
                object_id=self._equipment.scheme.id,
            )
        except Access.DoesNotExist:
            return None

    def equipment_presence(self) -> None:
        if not self._equipment:
            self.add_error('id', ObjectDoesNotExist(f'Equipment id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if self._equipment:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._equipment.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
