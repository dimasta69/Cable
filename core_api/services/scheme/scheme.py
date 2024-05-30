from django import forms
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status
from service_objects.fields import ModelField
from functools import lru_cache

from utils.services import ServiceWithResult
from models_app.models.scheme import Scheme
from models_app.models.user import User
from models_app.models.access import Access


class SchemeService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['access_presence', 'scheme_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.scheme
            self.response_status = status.HTTP_200_OK
        return self

    @property
    @lru_cache()
    def scheme(self):
        try:
            return Scheme.objects.get(id=self.cleaned_data['id'])
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
            self.add_error('id', ObjectDoesNotExist(f'Scheme id =  {self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self):
        if not self.access:
            self.add_error('current_user', PermissionDenied(f'Access to the schema id = {self.cleaned_data["id"]} '
                                                            'is not granted'))
            self.response_status = status.HTTP_403_FORBIDDEN
