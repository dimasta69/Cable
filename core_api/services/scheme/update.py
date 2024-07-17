from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError

from utils.services import ServiceWithResult
from django import forms
from service_objects.fields import ModelField
from functools import lru_cache

from models_app.models.scheme import Scheme
from models_app.models.user import User


class SchemeUpdateService(ServiceWithResult):
    current_user = ModelField(User)
    title = forms.CharField(required=True)
    id = forms.IntegerField(required=True)

    custom_validations = ['scheme_presence', 'access_presence', 'title_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_scheme()
            self.response_status = status.HTTP_200_OK
        return self

    def _update_scheme(self):
        scheme = self.scheme
        scheme.title = self.cleaned_data['title']
        scheme.save()
        return scheme

    @property
    @lru_cache()
    def scheme(self):
        try:
            return Scheme.objects.get(id=self.cleaned_data['id'])
        except Scheme.DoesNotExist:
            return None

    @property
    def scheme_list(self):
        try:
            return Scheme.objects.all()
        except Scheme.DoesNotExist:
            return Scheme.objects.none()

    def access_presence(self):
        if self.scheme and (self.scheme.creator != self.cleaned_data['current_user']):
            self.add_error('current_user', PermissionDenied(f'User {self.cleaned_data["current_user"]}access not '
                                                            f'allowed. Only the creator or administrator has access to '
                                                            f'change'))
            self.response_status = status.HTTP_403_FORBIDDEN

    def scheme_presence(self):
        if not self.scheme:
            self.add_error('id', ObjectDoesNotExist(f'Scheme id =  {self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def title_presence(self):
        if self.scheme:
            for scheme in self.scheme_list:
                if scheme.title.lower() == self.cleaned_data['title'].lower():
                    self.add_error('title', ValidationError("Title="
                                                            f"{self.cleaned_data['title']} already exists"))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
