from django import forms
from functools import lru_cache
from rest_framework import status

from core_api.utils.access_checker import scope_for_map
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Figure, User


class DeleteFigureService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    current_user = ModelField(User)
    id = forms.IntegerField(required=True)

    custom_validations = ["run_presence_checks", "access_presence"]
    presence_checks = [("_figure", "id", "Figure")]

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
