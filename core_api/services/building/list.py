from django import forms
from django.db.models import Q
from functools import lru_cache
from typing import Any
from django.db.models import QuerySet
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, Page
from cabel.settings import REST_FRAMEWORK

from core_api.utils.access_checker import AccessChecker, scope_for_scheme
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from models_app.models import Building, User, Scheme
from utils.fields import ModelField
from utils.services import ServiceWithResult


class BuildingListService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    filter_scheme_id = forms.IntegerField(required=True)
    search_filter = forms.CharField(required=False)
    current_user = ModelField(User)

    access_required_roles = AccessChecker.ROLES_READ
    custom_validations = ['run_presence_checks', 'access_presence']
    presence_checks = [("_scheme", "filter_scheme_id", "Scheme")]

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

    def get_access_scope(self):
        return scope_for_scheme(self._scheme)

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data['filter_scheme_id'])
        except Scheme.DoesNotExist:
            return None
