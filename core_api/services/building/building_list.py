from django import forms
from functools import lru_cache

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.building import Building
from models_app.models.scheme import Scheme


class BuildingListService(ServiceWithResult):
    filter_scheme_id = forms.IntegerField(required=True)

    custom_validations = ['scheme_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.building
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def building(self):
        try:
            return Building.objects.filter(scheme=self.scheme)
        except Building.DoesNotExist:
            return None

    @property
    @lru_cache()
    def scheme(self):
        try:
            return Scheme.objects.get(id=self.cleaned_data['filter_scheme_id'])
        except Scheme.DoesNotExist:
            return None

    def scheme_presence(self):
        if not self.scheme:
            self.add_error('filter_scheme_id', ObjectDoesNotExist('Scheme id='
                                                                  f'{self.cleaned_data["filter_scheme_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
