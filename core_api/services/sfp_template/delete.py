from django import forms
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from models_app.models import SfpTemplate
from models_app.models import Port


class DeleteSfpTemplateService(ServiceWithResult):
    id = forms.IntegerField(required=True)

    custom_validations = ['sfp_template_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.delete_sfp
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    @property
    def delete_sfp(self):
        if self.port:
            for port in self.port:
                if port.connection:
                    port.connection = None
                    port.connection.connection = None
                    port.save()

        self.sfp_template.delete()
        return None

    @property
    @lru_cache()
    def sfp_template(self):
        try:
            return SfpTemplate.objects.get(id=self.cleaned_data['id'])
        except SfpTemplate.DoesNotExist:
            return None

    @property
    @lru_cache()
    def port(self):
        try:
            return Port.objects.filter(sfp=self.sfp_template)
        except Port.DoesNotExist:
            return Port.objects.none()

    def sfp_template_presence(self):
        if self.cleaned_data['id']:
            if not self.sfp_template:
                self.add_error('id', ObjectDoesNotExist('Sfp template id='
                                                        f'{self.cleaned_data["id"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND
