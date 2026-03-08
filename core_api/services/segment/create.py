from django import forms
from functools import lru_cache
from rest_framework import status
from rest_framework.exceptions import NotFound

from core_api.utils.access_checker import scope_for_scheme
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Scheme, Segment, User


class CreateSegmentService(ResourceAccessMixin, ServiceWithResult):
    scheme_id = forms.IntegerField(required=True)
    name = forms.CharField(required=True)
    current_user = ModelField(User)

    custom_validations = ["scheme_presence", "access_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_segment
        return self

    @property
    def _create_segment(self) -> Segment:
        segment = Segment.objects.create(
            scheme=self._scheme,
            name=self.cleaned_data['name'],
        )
        return segment

    def get_access_scope(self):
        return scope_for_scheme(self._scheme)

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data["scheme_id"])
        except Scheme.DoesNotExist:
            return None

    def scheme_presence(self) -> None:
        if not self._scheme:
            self.add_error(
                "scheme_id",
                NotFound(
                    f"Scheme id={self.cleaned_data['scheme_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND
