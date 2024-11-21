from django import forms
from functools import lru_cache

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models.scheme import Scheme
from models_app.models.user import User
from models_app.models.access import Access


class CreateAccessService(ServiceWithResult):
    scheme_id = forms.IntegerField(required=True)
    user_id = forms.IntegerField(required=True)
    role = forms.CharField(required=True)
    current_user = ModelField(User)

    custom_validations = ['scheme_presence', 'role_presence', 'user_presence', 'access_presence', 'access_availability']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.create_access
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def create_access(self):
        return Access.objects.create(user=self.user, role=self.cleaned_data['role'], scheme=self.scheme)

    @property
    @lru_cache()
    def scheme(self):
        try:
            return Scheme.objects.get(id=self.cleaned_data['scheme_id'])
        except Scheme.DoesNotExist:
            return None

    @property
    @lru_cache()
    def user(self):
        try:
            return User.objects.get(id=self.cleaned_data['user_id'])
        except User.DoesNotExist:
            return None

    @property
    def access(self):
        try:
            return Access.objects.get(scheme=self.scheme, user=self.user)
        except Access.DoesNotExist:
            return None

    def scheme_presence(self):
        if self.cleaned_data['scheme_id']:
            if not self.scheme:
                self.add_error('filter_scheme_id', ObjectDoesNotExist('Scheme id='
                                                                      f'{self.cleaned_data["scheme_id"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def user_presence(self):
        if not self.user:
            self.add_error('user_id', ObjectDoesNotExist(f'User id={self.cleaned_data["user_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def role_presence(self):
        if self.cleaned_data['role']:
            if not self.cleaned_data.get('role') in ['Change', 'Read']:
                self.add_error('filter_role', ObjectDoesNotExist(f"Field in model with "
                                                                 f"{self.cleaned_data['role']} not found"))
                self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self):
        if self.scheme and self.user:
            if (self.scheme.creator != self.cleaned_data['current_user']
                    and not self.cleaned_data['current_user'].is_superuser):
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN

    def access_availability(self):
        if self.scheme and self.user:
            if self.access:
                self.add_error('current_user', PermissionDenied('The role already exists'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
