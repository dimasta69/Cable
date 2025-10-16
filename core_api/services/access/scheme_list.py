from functools import lru_cache
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Q
from rest_framework import status
from typing import List

from models_app.models import Access, User, Scheme
from utils.fields import ModelField
from utils.services import ServiceWithResult


class AccessListService(ServiceWithResult):
    current_user = ModelField(User)
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    filter_scheme_id = forms.IntegerField(required=True)
    filter_user_id = forms.IntegerField(required=False)
    filter_role = forms.CharField(required=False)
    search_filter = forms.CharField(required=False)

    custom_validations = ['scheme_presence', 'access_owner_or_superuser', 'filter_role_presence', 'user_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._access_filter_list
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _access_filter_list(self) -> List[Access]:
        access_list = self._access if self.cleaned_data['current_user'].is_superuser \
            else self._access.exclude(user=self.cleaned_data['current_user'])
        if self.cleaned_data['filter_role']:
            access_list = access_list.filter(role=self.cleaned_data['filter_role'])
        if self.cleaned_data["filter_user_id"]:
            access_list = access_list.filter(user__in=self.user)
        if self.cleaned_data['search_filter']:
            access_list = access_list.filter(
                Q(user__username__icontains=self.cleaned_data['search_filter']) |
                Q(object__title__icontains=self.cleaned_data['search_filter']) |
                Q(object__creator__username__icontains=self.cleaned_data['search_filter']) |
                Q(role__icontains=self.cleaned_data['search_filter'])
            )
        return access_list

    @property
    @lru_cache()
    def _access(self) -> List[Access]:
        try:
            return Access.objects.all()
        except Access.DoesNotExist:
            return Access.objects.none()

    @property
    @lru_cache()
    def user(self) -> User | None:
        try:
            return User.objects.filter(id=self.cleaned_data['filter_user_id'])
        except User.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data['filter_scheme_id'])
        except Scheme.DoesNotExist:
            return None

    def user_presence(self) -> None:
        if self.cleaned_data['filter_user_id']:
            if not self.user:
                self.add_error('filter_user_id', ObjectDoesNotExist('User id='
                                                                      f'{self.cleaned_data["filter_user_id"]} '
                                                                      'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def filter_role_presence(self) -> None:
        if self.cleaned_data['filter_role']:
            if not self.cleaned_data.get('filter_role') in ['Change', 'Creator', 'Read']:
                self.add_error('filter_role', ObjectDoesNotExist(f"Field in model with "
                                                                 f"{self.cleaned_data['filter_role']} not found"))
                self.response_status = status.HTTP_404_NOT_FOUND

    def scheme_presence(self) -> None:
        if self.cleaned_data['filter_scheme_id']:
            if not self._scheme:
                self.add_error('filter_scheme_id', ObjectDoesNotExist('Scheme id='
                                                                      f'{self.cleaned_data["filter_scheme_id"]} '
                                                                      'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def access_owner_or_superuser(self) -> None:
        if self._scheme and self._access:
            if (self._scheme.creator != self.cleaned_data['current_user']
                    and not self.cleaned_data['current_user'].is_superuser):
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._scheme.pk} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
