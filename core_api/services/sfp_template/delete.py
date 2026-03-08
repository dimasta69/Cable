from django import forms
from django.core.exceptions import PermissionDenied
from rest_framework import status
from functools import lru_cache
from typing import List

from core_api.utils.presence import PresenceChecksMixin
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import SfpTemplate, Port, User


class DeleteSfpTemplateService(PresenceChecksMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['run_presence_checks', 'is_superuser']
    presence_checks = [("_sfp_template", "id", "Sfp template")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._delete_sfp()
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    def _delete_sfp(self) -> None:
        for port in self._ports:
            if port.connection:
                port.connection = None
                port.connection.connection = None
        Port.objects.bulk_update(self._ports, ["sfp"])

        self._sfp_template.delete()

    @property
    @lru_cache()
    def _sfp_template(self) -> SfpTemplate | None:
        try:
            return SfpTemplate.objects.get(id=self.cleaned_data['id'])
        except SfpTemplate.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _ports(self) -> List[Port]:
        try:
            return Port.objects.filter(sfp=self._sfp_template)
        except Port.DoesNotExist:
            return Port.objects.none()

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied(
                    "User is not superuser"
                )
            )
            self.response_status = status.HTTP_403_FORBIDDEN
