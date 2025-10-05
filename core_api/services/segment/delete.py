from django.db.models import Q
from django import forms
from functools import lru_cache

from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotFound

from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Access, User, Segment, Scheme

class DeleteSegmentService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ["segment_presence", "access_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._segment.delete()
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    @property
    @lru_cache()
    def _segment(self) -> Segment | None:
        try:
            return Segment.objects.select_related("scheme").get(id=self.cleaned_data['id'])
        except Segment.DoesNotExist:
            return None

    @property
    def _access(self):
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        try:
            return Access.objects.filter(
                Q(
                    object_type=scheme_content_type,
                    object_id=self._segment.scheme.pk,
                ),
            ).filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator']
            )
        except Access.DoesNotExist:
            return None

    def segment_presence(self) -> None:
        if not self._segment:
            self.add_error(
                "id",
                NotFound(
                    f"Segment id={self.cleaned_data['id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if self._segment:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schem id = '
                                                                f'{self._segment.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
