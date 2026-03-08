from django import forms
from functools import lru_cache
from rest_framework.exceptions import NotFound
from rest_framework import status
from typing import List

from core_api.utils.access_checker import AccessChecker, scope_for_map
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Figure, User, SchemeMap


class FigureListService(ResourceAccessMixin, ServiceWithResult):
    current_user = ModelField(User)
    filter_map_id = forms.IntegerField(required=True)

    access_required_roles = AccessChecker.ROLES_READ
    custom_validations = ["access_presence", "map_presence"]

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

    def map_presence(self) -> None:
        if not self._map:
            self.add_error(
                "filter_map_id",
                NotFound(
                    f"Map id={self.cleaned_data['filter_map_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND
