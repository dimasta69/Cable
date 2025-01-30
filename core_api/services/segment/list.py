from django import forms
from typing import List
from functools import lru_cache

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Segment, Scheme, Access, User


class SegmentListService(ServiceWithResult):
    scheme_id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)

    custom_validations = ["scheme_presence", "access_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._segments
        return self

    @property
    def _segments(self) -> List[Segment]:
        try:
            return Segment.objects.filter(scheme=self._scheme)
        except Segment.DoesNotExist:
            return Segment.objects.none()

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data["scheme_id"])
        except Scheme.DoesNotExist:
            return None

    @property
    def _access(self):
        try:
            return Access.objects.filter(
                Q(
                    object_type=self.scheme_content_type,
                    object_id=self._scheme.pk,
                ),
            ).filter(
                user=self.cleaned_data['current_user'],
            )
        except Access.DoesNotExist:
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

    def access_presence(self) -> None:
        if self._scheme:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schem id = '
                                                                f'{self._scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
