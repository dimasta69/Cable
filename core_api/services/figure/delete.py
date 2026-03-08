from django import forms
from functools import lru_cache
from rest_framework.exceptions import NotFound
from rest_framework import status

from core_api.utils.access_checker import scope_for_map
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Figure, User


class DeleteFigureService(ResourceAccessMixin, ServiceWithResult):
    current_user = ModelField(User)
    id = forms.IntegerField(required=True)

    custom_validations = ["access_presence", "figure_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._delete_figure()
        return self

    def _delete_figure(self) -> None:
        self._figure.delete()

    def get_access_scope(self):
        return scope_for_map(self._figure.schemes) if self._figure else None

    @property
    @lru_cache()
    def _figure(self) -> Figure | None:
        try:
            return Figure.objects.select_related('schemes', 'schemes__scheme').get(
                id=self.cleaned_data['id']
            )
        except Figure.DoesNotExist:
            return None

    def figure_presence(self) -> None:
        if not self._figure:
            self.add_error(
                "id",
                NotFound(
                    f"Figure id={self.cleaned_data['id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND
