from django import forms
from functools import lru_cache
from rest_framework import status

from core_api.utils.access_checker import scope_for_segment
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Vlan, User, Segment


class CreateVlanService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    name = forms.CharField(required=True)
    id_name = forms.CharField(required=True)
    segment_id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['run_presence_checks', 'access_presence']
    presence_checks = [("_segment", "segment_id", "Segment")]

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
