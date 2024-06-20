from django import forms
from django.core.exceptions import ObjectDoesNotExist
from functools import lru_cache
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.sfp_template import SfpTemplate


class SfpTemplateService(ServiceWithResult):
    id = forms.IntegerField(required=True)

    custom_validations = ['sfp_template_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.sfp_template
            self.response_status = status.HTTP_200_OK
        return self

    @property
    @lru_cache()
    def sfp_template(self):
        try:
            return SfpTemplate.objects.get(id=self.cleaned_data['id'])
        except SfpTemplate.DoesNotExist:
            return None

    def sfp_template_presence(self):
        if not self.sfp_template:
            self.add_error('id', ObjectDoesNotExist(f'Sfp template id={self.cleaned_data["id"]} is not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
