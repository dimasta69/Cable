from django import forms
from rest_framework import status
from functools import lru_cache

from core_api.utils.access_checker import scope_for_scheme
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.services import ServiceWithResult
from models_app.models import User, Scheme, SchemeMap
from utils.fields import ModelField


class CreateMapService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    name = forms.CharField(required=True)
    scheme_id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['run_presence_checks', 'access_presence']
    presence_checks = [("_scheme", "scheme_id", "Scheme")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_scheme_map
        return self

    @property
    def _create_scheme_map(self) -> SchemeMap:
        return SchemeMap.objects.create(
            name=self.cleaned_data['name'],
            scheme=self._scheme,
        )

    def get_access_scope(self):
        return scope_for_scheme(self._scheme)

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data['scheme_id'])
        except Scheme.DoesNotExist:
            return None
