from django import forms
from rest_framework import status
from functools import lru_cache

from rest_framework.exceptions import NotFound

from utils.errors import ValidationError
from utils.services import ServiceWithResult
from models_app.models.port_template import PortTemplate


class UpdatePortTemplateService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    name = forms.CharField(required=True)

    custom_validations = ['name_presence', 'port_template_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.update_port_template
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def update_port_template(self):
        port_template = self.port_template
        port_template.name = self.cleaned_data['name']
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

    def name_presence(self):
        if self.port_template:
            for port in self.port_template_list:
                if port.name == self.cleaned_data['name']:
                    self.add_error('name', ValidationError(f'Field with title={self.cleaned_data["name"]}'
                                                           ' already exists'))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def port_template_presence(self):
        if not self.port_template:
            self.add_error('id', NotFound(f'Port template id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
