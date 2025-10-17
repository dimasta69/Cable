from django import forms
from functools import lru_cache

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import User, Access, Scheme


class UpdateAccessService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    scheme_id = forms.IntegerField(required=True)
    role = forms.CharField(required=True)
    current_user = ModelField(User)

    custom_validations = [
        'access_creator', 'access_presence', 'role_presence', 'scheme_presence', 'access_owner_or_superuser',
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_access
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _update_access(self) -> Access:
        access = self._access
        if self.cleaned_data['role']:
            access.role = self.cleaned_data['role']
        access.save()
        return access

    @property
    @lru_cache()
    def _access(self) -> Access | None:
        try:
            return Access.objects.get(id=self.cleaned_data['id'])
        except Access.DoesNotExist:
            return None

    @property
    @lru_cache()
    def scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data['scheme_id'])
        except Scheme.DoesNotExist:
            return None

    def access_creator(self) -> None:
        if self._access:
            if self._access.role == 'Creator':
                self.add_error('id', PermissionDenied("You can't delete the creator"))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def access_presence(self) -> None:
        if not self._access:
            self.add_error('id', ObjectDoesNotExist(f'Access id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_owner_or_superuser(self) -> None:
        if self._access and self.scheme:
            if (self.scheme.creator != self.cleaned_data['current_user']
                    and not self.cleaned_data['current_user'].is_superuser):
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._access.object.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN

    def role_presence(self) -> None:
        if self.cleaned_data['role']:
            if not self.cleaned_data.get('role') in ['Change', 'Read']:
                self.add_error('filter_role', ObjectDoesNotExist(f"Field in model with "
                                                                 f"{self.cleaned_data['role']} not found"))
                self.response_status = status.HTTP_404_NOT_FOUND

    def scheme_presence(self) -> None:
        if not self.scheme:
            self.add_error("scheme_id", ObjectDoesNotExist(
                f"Scheme id = {self.cleaned_data['scheme_id']} not found"
            ))
            self.response_status = status.HTTP_404_NOT_FOUND
