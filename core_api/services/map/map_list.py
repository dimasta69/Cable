from django import forms
from functools import lru_cache
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from typing import List

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import User, Access, Scheme, SchemeMap


class MapListService(ServiceWithResult):
    scheme_id = forms.IntegerField(required=True)
    search_filter = forms.CharField(required=False)
    current_user = ModelField(User)

    custom_validations = ['scheme_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._maps_filter
        return self

    @property
    def _maps_filter(self) -> List[SchemeMap]:
        maps = self._maps
        if self.cleaned_data['search_filter']:
            maps = maps.filter(name__icontains=self.cleaned_data['search_filter'])
        return maps

    @property
    def _maps(self) -> List[SchemeMap]:
        try:
            return SchemeMap.objects.filter(scheme=self._scheme)
        except SchemeMap.DoesNotExist:
            return SchemeMap.objects.none()

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data['scheme_id'])
        except Scheme.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        try:
            return Access.objects.get(user=self.cleaned_data['current_user'], scheme=self.scheme)
        except Access.DoesNotExist:
            return None

    def access_presence(self) -> None:
        if self._scheme:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.cleaned_data["scheme_id"]} is '
                                                                'not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
