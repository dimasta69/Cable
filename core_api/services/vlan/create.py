from django import forms
from functools import lru_cache
from rest_framework import status
from rest_framework.exceptions import NotFound

from core_api.utils.access_checker import scope_for_segment
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Vlan, User, Segment


class CreateVlanService(ResourceAccessMixin, ServiceWithResult):
    name = forms.CharField(required=True)
    id_name = forms.CharField(required=True)
    segment_id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['segment_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_vlan
        return self

    @property
    def _create_vlan(self) -> Vlan:
        return Vlan.objects.create(
            id_name=self.cleaned_data['id_name'],
            name=self.cleaned_data['name'],
            segment=self._segment,
        )

    def get_access_scope(self):
        return scope_for_segment(self._segment)

    @property
    @lru_cache()
    def _segment(self) -> Segment | None:
        try:
            return Segment.objects.select_related('scheme').get(id=self.cleaned_data["segment_id"])
        except Segment.DoesNotExist:
            return None

    def segment_presence(self) -> None:
        if not self._segment:
            self.add_error(
                "segment_id",
                NotFound(
                    f"Segment with id={self.cleaned_data['segment_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND
