from django import forms
from typing import List
from functools import lru_cache
from django.db.models import Q
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage

from core_api.utils.access_checker import AccessChecker, scope_for_scheme
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from cabel.settings import REST_FRAMEWORK
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Segment, Scheme, User


class SegmentListService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    page = forms.IntegerField(required=False)
    per_page = forms.IntegerField(required=False)
    scheme_id = forms.IntegerField(required=True)
    search_filter = forms.CharField(required=False)
    current_user = ModelField(User)

    access_required_roles = AccessChecker.ROLES_READ
    custom_validations = ["run_presence_checks", "access_presence"]
    presence_checks = [("_scheme", "scheme_id", "Scheme")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.segment_pagination
        return self

    @property
    def segment_pagination(self) -> Paginator:
        try:
            return (Paginator(self.filter_segment, per_page=(self.cleaned_data['per_page'] or
                                                             REST_FRAMEWORK['PAGE_SIZE'])).
                    page(self.cleaned_data['page'] or 1))
        except EmptyPage:
            return (Paginator(self.filter_segment, per_page=(self.cleaned_data['per_page'] or
                                                             REST_FRAMEWORK['PAGE_SIZE'])).page(1))

    @property
    def filter_segment(self) -> List[Segment]:
        segments = self._segments
        if self.cleaned_data["search_filter"]:
            segments = segments.filter(
                Q(name__icontains=self.cleaned_data["search_filter"])
            )
        return segments

    @property
    def _segments(self) -> List[Segment]:
        try:
            return Segment.objects.filter(scheme=self._scheme)
        except Segment.DoesNotExist:
            return Segment.objects.none()

    def get_access_scope(self):
        return scope_for_scheme(self._scheme)

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data["scheme_id"])
        except Scheme.DoesNotExist:
            return None
