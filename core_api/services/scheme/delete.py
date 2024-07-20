from rest_framework import status
from functools import lru_cache

from models_app.models import Access
from utils.services import ServiceWithResult
from django import forms
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from service_objects.fields import ModelField

from models_app.models.scheme import Scheme
from models_app.models.user import User


class SchemeDeleteService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['scheme_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.delete_scheme
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    @property
    def delete_scheme(self):
        self.scheme.delete()
        return None

    @property
    @lru_cache()
    def scheme(self):
        try:
            return Scheme.objects.get(id=self.cleaned_data['id'])
        except Scheme.DoesNotExist:
            return None

    def scheme_presence(self):
        if not self.scheme:
            self.add_error('id', ObjectDoesNotExist(f'Scheme id =  {self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self):
        if (self.scheme and (self.scheme.creator != self.cleaned_data['current_user']) and not
        self.cleaned_data['current_user'].is_superuser):
            self.add_error('current_user', PermissionDenied(f'User {self.cleaned_data["current_user"]}access not '
                                                            f'allowed. Only the creator or administrator has access to '
                                                            f'delete'))
            self.response_status = status.HTTP_403_FORBIDDEN
