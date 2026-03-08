from django import forms
from functools import lru_cache
from rest_framework import status
from typing import List

from core_api.utils.access_checker import AccessChecker, scope_for_map
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Figure, User, SchemeMap


class FigureListService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    current_user = ModelField(User)
    filter_map_id = forms.IntegerField(required=True)

    access_required_roles = AccessChecker.ROLES_READ
    custom_validations = ["run_presence_checks", "access_presence"]
    presence_checks = [("_map", "filter_map_id", "Map")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._figures
        return self

    @property
    def _figures(self) -> List[Figure]:
        try:
            return Figure.objects.filter(schemes=self._map)
        except Figure.DoesNotExist:
            return Figure.objects.none()

    def get_access_scope(self):
        return scope_for_map(self._map)

    @property
    @lru_cache()
    def _map(self) -> SchemeMap | None:
        try:
            return SchemeMap.objects.select_related('scheme').get(id=self.cleaned_data['filter_map_id'])
        except SchemeMap.DoesNotExist:
            return None
