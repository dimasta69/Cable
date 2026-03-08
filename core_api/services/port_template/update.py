from django import forms
from rest_framework import status
from functools import lru_cache

from rest_framework.exceptions import PermissionDenied

from core_api.utils.presence import PresenceChecksMixin
from utils.errors import ValidationError
from utils.services import ServiceWithResult
from utils.fields import ListIntegerField, ModelField
from models_app.models import PortTemplate, User, Speed


class UpdatePortTemplateService(PresenceChecksMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    name = forms.CharField(required=False)
    unit = ListIntegerField(required=False)
    lines = forms.IntegerField(required=False)
    speed_list = ListIntegerField(required=False)
    current_user = ModelField(User)

    custom_validations = [
        'run_presence_checks', 'name_presence', 'count_unit', 'lines_presence', 'is_superuser',
    ]
    presence_checks = [("port_template", "id", "Port template")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.update_port_template
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def update_port_template(self):
        port_template = self.port_template
        if self.cleaned_data['name']:
            port_template.name = self.cleaned_data['name']
        if self.cleaned_data['unit']:
            port_template.unit = self.cleaned_data['unit']
        if self.cleaned_data['lines']:
            port_template.lines = self.cleaned_data['lines']
        port_template.save()
        return port_template

    @property
    @lru_cache()
    def port_template_list(self):
        try:
            return PortTemplate.objects.all()
        except PortTemplate.DoesNotExist:
            return PortTemplate.objects.none()

    @property
    @lru_cache()
    def port_template(self):
        try:
            return self.port_template_list.get(id=self.cleaned_data['id'])
        except PortTemplate.DoesNotExist:
            return None

    @property
    @lru_cache()
    def speeds(self):
        try:
            return Speed.objects.filter(id__in=self.cleaned_data['speed_list']).only('id')
        except Speed.DoesNotExist:
            return None

    def name_presence(self):
        if self.port_template:
            for port in self.port_template_list:
                if port.name == self.cleaned_data['name']:
                    self.add_error('name', ValidationError(f'Field with title={self.cleaned_data["name"]}'
                                                           ' already exists'))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def count_unit(self):
        if self.cleaned_data['unit']:
            if self.port_template.equipment_tmp.number_of_units < len(self.cleaned_data['unit']):
                self.add_error('unit', ValidationError('The number of units does not match'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def lines_presence(self):
        if self.cleaned_data['lines'] or self.cleaned_data['unit']:
            if (len((self.cleaned_data['unit']) or self.port_template.unit) / (self.cleaned_data['lines'] or
                                                                               self.port_template.lines)) < 0.5:
                self.add_error('unit', ValidationError('Еhe number of lines per unit should not exceed 2'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied(
                    "User is not superuser"
                )
            )
