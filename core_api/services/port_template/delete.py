from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from django import forms

from models_app.models.port_template import PortTemplate


class PortTemplateDeleteService(ServiceWithResult):
    id = forms.IntegerField(required=True)

    custom_validations = ['port_template_presence']

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

    def port_template_presence(self):
        if not self.port_template:
            self.add_error('id', ObjectDoesNotExist(f'Port template id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
