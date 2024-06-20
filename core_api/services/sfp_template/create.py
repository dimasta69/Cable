from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from functools import lru_cache

from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.sfp_template import SfpTemplate
from models_app.models.manufacturer import Manufacturer


class CreateSfpTemplateService(ServiceWithResult):
    manufacturer_id = forms.IntegerField(required=True)
    name = forms.CharField(required=True)
    speed = forms.IntegerField(required=True)

    custom_validations = ['manufacturer_presence', 'name_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.create_sfp_template
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def create_sfp_template(self):
        return SfpTemplate.objects.create(manufacturer=self.manufacturer,
                                          name=self.cleaned_data['name'],
                                          speed=self.cleaned_data['speed'])

    @property
    def sfp_template_list(self):
        try:
            return SfpTemplate.objects.all()
        except SfpTemplate.DoesNotExist:
            return SfpTemplate.objects.none()

    @property
    @lru_cache()
    def manufacturer(self):
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['manufacturer_id'])
        except Manufacturer.DoesNotExist:
            return None

    def manufacturer_presence(self):
        if not self.manufacturer:
            self.add_error('manufacturer_id', ObjectDoesNotExist('Manufacturer id='
                                                                 f'{self.cleaned_data["manufacturer_id"]} '
                                                                 'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def name_presence(self):
        for sfp_template in self.sfp_template_list:
            if self.cleaned_data['name'].lower() == sfp_template.name.lower():
                self.add_error('name', ValidationError(f'Field with name={self.cleaned_data["name"]}'
                                                       ' already exists'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
