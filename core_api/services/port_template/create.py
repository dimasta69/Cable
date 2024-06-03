from django import forms
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.exceptions import NotFound

from utils.services import ServiceWithResult
from models_app.models.port_template import PortTemplate


class CreatePortTemplateService(ServiceWithResult):
    name = forms.CharField(required=True)

    custom_validations = ['name_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.create_port_template
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def create_port_template(self):
        return PortTemplate.objects.create(name=self.cleaned_data['name'])

    @property
    def port_template(self):
        try:
            return PortTemplate.objects.all()
        except PortTemplate.DoesNotExist:
            return None

    def name_presence(self):
        for port in self.port_template:
            if port.name == self.cleaned_data['name']:
                self.add_error('name', ValidationError(f'Field with title={self.cleaned_data["name"]}'
                                                       ' already exists'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
