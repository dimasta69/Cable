from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from functools import lru_cache
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied

from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Vlan, User, Segment, Access, Scheme


class CreateVlanService(ServiceWithResult):
    name = forms.CharField(required=True)
    id_name = forms.CharField(required=True)
    segment_id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['segment_presence', 'access_presence', ]

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

    @property
    @lru_cache()
    def _segment(self) -> Segment | None:
        try:
            return Segment.objects.get(id=self.cleaned_data["segment_id"])
        except Segment.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        segment_content_type = ContentType.objects.get_for_model(Segment)
        try:
            return Access.objects.filter(
                Q(
                    object_type=scheme_content_type,
                    object_id=self._segment.scheme.pk,
                ) |
                Q(
                    object_type=segment_content_type,
                    object_id=self._segment.pk,
                )
            ).filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator']
            )
        except Access.DoesNotExist:
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

    def access_presence(self) -> None:
        if not self._access:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schem id = '
                                                                f'{self._segment.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
