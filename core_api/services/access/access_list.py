from functools import lru_cache
from django import forms
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from rest_framework import status

from cabel.settings import REST_FRAMEWORK
from models_app.models import Access, User, Scheme
from utils.fields import ModelField
from utils.services import ServiceWithResult


class AccessListService(ServiceWithResult):
    current_user = ModelField(User)
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    filter_scheme_id = forms.IntegerField(required=True)
    filter_role = forms.CharField(required=False)
    search_filter = forms.CharField(required=False)

    custom_validations = ['scheme_presence', 'access_presence', 'filter_role_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.access_filter_list
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def access_filter_list(self):
        access_list = self.access if self.cleaned_data['current_user'].is_superuser \
            else self.access.exclude(user=self.cleaned_data['current_user'])
        if self.cleaned_data['filter_role']:
            access_list = access_list.filter(role=self.cleaned_data['filter_role'])
        if self.cleaned_data['search_filter']:
            access_list = access_list.filter(
                Q(user__username__icontains=self.cleaned_data['search_filter']) |
                Q(scheme__title__icontains=self.cleaned_data['search_filter']) |
                Q(scheme__creator__username__icontains=self.cleaned_data['search_filter']) |
                Q(role__icontains=self.cleaned_data['search_filter'])
            )
        return access_list

    @property
    @lru_cache()
    def access(self):
        try:
            return Access.objects.filter(scheme=self.scheme)
        except Access.DoesNotExist:
            return None

    @property
    @lru_cache()
    def scheme(self):
        try:
            return Scheme.objects.get(id=self.cleaned_data['filter_scheme_id'])
        except Scheme.DoesNotExist:
            return None

    def filter_role_presence(self):
        if self.cleaned_data['filter_role']:
            if not self.cleaned_data.get('filter_role') in ['Change', 'Creator', 'Read']:
                self.add_error('filter_role', ObjectDoesNotExist(f"Field in model with "
                                                                 f"{self.cleaned_data['filter_role']} not found"))
                self.response_status = status.HTTP_404_NOT_FOUND

    def scheme_presence(self):
        if self.cleaned_data['filter_scheme_id']:
            if not self.scheme:
                self.add_error('filter_scheme_id', ObjectDoesNotExist('Scheme id='
                                                                      f'{self.cleaned_data["filter_scheme_id"]} '
                                                                      'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self):
        if self.scheme and self.access:
            if (self.scheme.creator != self.cleaned_data['current_user']
                    and not self.cleaned_data['current_user'].is_superuser):
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
