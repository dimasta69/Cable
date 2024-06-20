from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from models_app.models.sfp_template import SfpTemplate


class DeleteSfpTemplateService(ServiceWithResult):
    id = forms.IntegerField(required=True)

    custom_validations = ['sfp_template_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.delete_sfp_template
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    @property
    def delete_sfp_template(self):
        self.sfp_template.delete()
        return None

    @property
    @lru_cache()
    def sfp_template(self):
        try:
            return SfpTemplate.objects.get(id=self.cleaned_data['id'])
        except SfpTemplate.DoesNotExist:
            return None

    def sfp_template_presence(self):
        if not self.sfp_template:
            self.add_error('id', ObjectDoesNotExist(f'Sfp Template id =  {self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
