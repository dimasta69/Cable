from django import forms
from functools import lru_cache
from rest_framework import status
from rest_framework.exceptions import NotFound
from typing import List

from core_api.utils.access_checker import AccessChecker, scope_for_scheme
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import User, Scheme, SchemeMap


class MapListService(ResourceAccessMixin, ServiceWithResult):
    scheme_id = forms.IntegerField(required=True)
    search_filter = forms.CharField(required=False)
    current_user = ModelField(User)

    access_required_roles = AccessChecker.ROLES_READ
    custom_validations = ['scheme_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._maps_filter
        return self

    @property
    def _maps_filter(self) -> List[SchemeMap]:
        maps = self._maps
        if self.cleaned_data.get('search_filter'):
            maps = maps.filter(name__icontains=self.cleaned_data['search_filter'])
        return maps

    @property
    def _maps(self) -> List[SchemeMap]:
        try:
            return SchemeMap.objects.filter(scheme=self._scheme)
        except SchemeMap.DoesNotExist:
            return SchemeMap.objects.none()

    def get_access_scope(self):
        return scope_for_scheme(self._scheme)

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data['scheme_id'])
        except Scheme.DoesNotExist:
            return None

    def scheme_presence(self) -> None:
        if not self._scheme:
            self.add_error(
                "scheme_id",
                NotFound(
                    f"Scheme with id = {self.cleaned_data['scheme_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND
