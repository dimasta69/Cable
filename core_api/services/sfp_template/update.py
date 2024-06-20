from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from functools import lru_cache

from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.sfp_template import SfpTemplate


class UpdateSfpTemplateService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    name = forms.CharField(required=False)
    speed = forms.IntegerField(required=False)

    custom_validations = ['name_presence', 'sfp_template_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.update_sfp_template
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def update_sfp_template(self):
        sfp_template = self.sfp_template_list.get(id=self.cleaned_data['id'])
        if self.cleaned_data['name']:
            sfp_template.name = self.cleaned_data['name']
        if self.cleaned_data['speed']:
            sfp_template.speed = self.cleaned_data['speed']
        sfp_template.save()
        return sfp_template

    @property
    @lru_cache()
    def sfp_template_list(self):
        try:
            return SfpTemplate.objects.all()
        except SfpTemplate.DoesNotExist:
            return SfpTemplate.objects.none()

    def name_presence(self):
        if self.cleaned_data['name']:
            for sfp_template in self.sfp_template_list:
                if self.cleaned_data['name'].lower() == sfp_template.name.lower():
                    self.add_error('name', ValidationError(f'Field with name={self.cleaned_data["name"]}'
                                                           ' already exists'))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def sfp_template_presence(self):
        if not self.sfp_template_list.get(id=self.cleaned_data['id']):
            self.add_error('id', ObjectDoesNotExist(f'Sfp template id={self.cleaned_data["id"]} is not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
