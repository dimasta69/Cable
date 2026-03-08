from django.core.exceptions import PermissionDenied
from rest_framework import status
from functools import lru_cache

from core_api.utils.presence import PresenceChecksMixin
from utils.services import ServiceWithResult
from utils.fields import ModelField
from django import forms

from models_app.models import PortTemplate, User


class PortTemplateDeleteService(PresenceChecksMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['run_presence_checks', 'is_superuser']
    presence_checks = [("port_template", "id", "Port template")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.delete_port_template
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    @property
    def delete_port_template(self):
        self.port_template.delete()
        return None

    @property
    @lru_cache()
    def port_template(self):
        try:
            return PortTemplate.objects.get(id=self.cleaned_data['id'])
        except PortTemplate.DoesNotExist:
            return None

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied(
                    "User is not superuser"
                )
            )
