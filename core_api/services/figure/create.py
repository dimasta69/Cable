from django import forms
from rest_framework.exceptions import NotFound
from rest_framework import status

from core_api.utils.access_checker import scope_for_map
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Figure, User, SchemeMap
from models_app.models.schemes.figure.models import type_choice


class CreateFigureService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    current_user = ModelField(User)
    map_id = forms.IntegerField(required=True)
    title = forms.CharField(required=True)
    type = forms.CharField(required=True)
    x = forms.FloatField(required=True)
    y = forms.FloatField(required=True)
    width = forms.IntegerField(min_value=1)
    height = forms.IntegerField(min_value=1)

    custom_validations = ["run_presence_checks", "type_presence", "access_presence"]
    presence_checks = [("_map", "map_id", "Map")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_figure
        return self

    @property
    def _create_figure(self) -> Figure:
        return Figure.objects.create(
            title=self.cleaned_data['title'],
            schemes=self._map,
            type=self.cleaned_data['type'],
            x=self.cleaned_data['x'],
            y=self.cleaned_data['y'],
            width=self.cleaned_data['width'],
            height=self.cleaned_data['height'],
        )

    def get_access_scope(self):
        return scope_for_map(self._map)

    @property
    def _map(self) -> SchemeMap | None:
        try:
            return SchemeMap.objects.select_related('scheme').get(id=self.cleaned_data['map_id'])
        except SchemeMap.DoesNotExist:
            return None

    def type_presence(self) -> None:
        if not [t[0] for t in type_choice if t[0] == self.cleaned_data['type']]:
            self.add_error(
                "type",
                NotFound(
                    f"Type ={self.cleaned_data['type']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND
