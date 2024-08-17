from django import forms
from functools import lru_cache

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status

from models_app.models import Access
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models.building import Building
from models_app.models.user import User
from models_app.models.scheme import Scheme


class BuildingListService(ServiceWithResult):
    filter_scheme_id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['access_presence', 'scheme_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.building
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def building(self):
        try:
            return Building.objects.filter(scheme=self.scheme).select_related('scheme')
        except Building.DoesNotExist:
            return None

    @property
    @lru_cache()
    def scheme(self):
        try:
            return Scheme.objects.get(id=self.cleaned_data['filter_scheme_id'])
        except Scheme.DoesNotExist:
            return None

    @property
    def access(self):
        try:
            return Access.objects.get(user=self.cleaned_data['current_user'], scheme=self.scheme)
        except Access.DoesNotExist:
            return None

    def scheme_presence(self):
        if not self.scheme:
            self.add_error('filter_scheme_id', ObjectDoesNotExist('Scheme id='
                                                                  f'{self.cleaned_data["filter_scheme_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self):
        if self.scheme:
            if not self.access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.cleaned_data["filter_scheme_id"]} is '
                                                                'not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
