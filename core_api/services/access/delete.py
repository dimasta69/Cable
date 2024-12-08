from django import forms
from functools import lru_cache

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import User
from models_app.models import Access


class DeleteAccessService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['access_creator', 'access_presence', 'access_role']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.delete_access
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    @property
    def delete_access(self):
        self.access.delete()
        return None

    @property
    @lru_cache()
    def access(self):
        try:
            return Access.objects.get(id=self.cleaned_data['id'])
        except Access.DoesNotExist:
            return None

    def access_creator(self):
        if self.access:
            if self.access.role == 'Creator':
                self.add_error('id', PermissionDenied("You can't delete the creator"))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def access_presence(self):
        if not self.access:
            self.add_error('id', ObjectDoesNotExist(f'Access id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_role(self):
        if self.access:
            if (self.access.scheme.creator != self.cleaned_data['current_user']
                    and not self.cleaned_data['current_user'].is_superuser):
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.access.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
