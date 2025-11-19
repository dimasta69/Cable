from django import forms
from django.db.models import Q
from functools import lru_cache
from typing import Any
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import QuerySet
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, Page
from cabel.settings import REST_FRAMEWORK

from models_app.models import Access, Building, User, Scheme
from utils.fields import ModelField
from utils.services import ServiceWithResult


class BuildingListService(ServiceWithResult):
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    filter_scheme_id = forms.IntegerField(required=True)
    search_filter = forms.CharField(required=False)
    current_user = ModelField(User)

    custom_validations = ['access_presence', 'scheme_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.building_pagination
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def building_pagination(self) -> Page[Any]:
        try:
            return (Paginator(self.building_filter, per_page=(self.cleaned_data['per_page'] or
                                                        REST_FRAMEWORK['PAGE_SIZE'])).
                    page(self.cleaned_data['page'] or 1))
        except EmptyPage:
            return (Paginator(self.building_filter, per_page=(self.cleaned_data['per_page'] or
                                                        REST_FRAMEWORK['PAGE_SIZE'])).page(1))
    @property
    def building_filter(self) -> QuerySet[Building, Building]:
        buildings = self._building
        if self.cleaned_data['search_filter']:
            buildings = buildings.filter(Q(name__icontains=self.cleaned_data['search_filter']))
        return buildings

    @property
    def _building(self) -> QuerySet[Building, Building]:
        try:
            return Building.objects.filter(scheme=self._scheme).select_related('scheme')
        except Building.DoesNotExist:
            return Building.objects.none()

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data['filter_scheme_id'])
        except Scheme.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)

        try:
            return Access.objects.get(
                user=self.cleaned_data['current_user'],
                object_type=scheme_content_type,
                object_id=self._scheme.pk,
            )
        except Access.DoesNotExist:
            return None

    def scheme_presence(self) -> None:
        if not self._scheme:
            self.add_error('filter_scheme_id', ObjectDoesNotExist('Scheme id='
                                                                  f'{self.cleaned_data["filter_scheme_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if self._scheme:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.cleaned_data["filter_scheme_id"]} is '
                                                                'not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
