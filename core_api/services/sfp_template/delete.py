from django import forms
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status
from functools import lru_cache
from typing import List

from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import SfpTemplate, Port, User


class DeleteSfpTemplateService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['sfp_template_presence', 'is_superuser']

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

    def sfp_template_presence(self) -> None:
        if self.cleaned_data['id']:
            if not self._sfp_template:
                self.add_error('id', ObjectDoesNotExist('Sfp template id='
                                                        f'{self.cleaned_data["id"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied(
                    "User is not superuser"
                )
            )
            self.response_status = status.HTTP_403_FORBIDDEN
