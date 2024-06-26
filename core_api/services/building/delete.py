from functools import lru_cache

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.building import Building


class DeleteBuildingService(ServiceWithResult):
    id = forms.IntegerField(required=True)

    custom_validations = ['building_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.delete_building
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    @property
    def delete_building(self):
        self.building.delete()
        return None

    @property
    @lru_cache()
    def building(self):
        try:
            return Building.objects.get(id=self.cleaned_data['id'])
        except Building.DoesNotExist:
            return None

    def building_presence(self):
        if not self.building:
            self.add_error('id', ObjectDoesNotExist('Building id='
                                                    f'{self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
