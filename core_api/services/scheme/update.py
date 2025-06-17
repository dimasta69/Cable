from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError

from utils.services import ServiceWithResult
from django import forms
from service_objects.fields import ModelField
from functools import lru_cache

from models_app.models import Scheme
from models_app.models import User


class SchemeUpdateService(ServiceWithResult):
    current_user = ModelField(User)
    title = forms.CharField(required=True)
    id = forms.IntegerField(required=True)

    custom_validations = ['scheme_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_scheme
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _update_scheme(self) -> Scheme:
        scheme = self._scheme
        scheme.title = self.cleaned_data['title']
        scheme.save()
        return scheme

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data['id'])
        except Scheme.DoesNotExist:
            return None

    def access_presence(self) -> None:
        if (self._scheme and (self._scheme.creator != self.cleaned_data['current_user']) and not
                self.cleaned_data['current_user'].is_superuser):
            self.add_error('current_user', PermissionDenied(f'User {self.cleaned_data["current_user"]}access not '
                                                            f'allowed. Only the creator or administrator has access to '
                                                            f'delete'))
            self.response_status = status.HTTP_403_FORBIDDEN

    def scheme_presence(self) -> None:
        if not self._scheme:
            self.add_error('id', ObjectDoesNotExist(f'Scheme id =  {self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
