from django import forms
from functools import lru_cache

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Scheme, Segment, Access, User


class CreateSegmentService(ServiceWithResult):
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

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data["scheme_id"])
        except Scheme.DoesNotExist:
            return None

    @property
    def _access(self):
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        try:
            return Access.objects.filter(
                Q(
                    object_type=scheme_content_type,
                    object_id=self._scheme.pk,
                ),
            ).filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator']
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
