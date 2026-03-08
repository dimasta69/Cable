from django import forms
from rest_framework import status
from rest_framework.exceptions import NotFound
from functools import lru_cache

from core_api.utils.access_checker import scope_for_segment
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Segment, User


class DeleteSegmentService(ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ["segment_presence", "access_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._segment.delete()
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    def get_access_scope(self):
        return scope_for_segment(self._segment)

    @property
    @lru_cache()
    def _segment(self) -> Segment | None:
        try:
            return Segment.objects.select_related("scheme").get(id=self.cleaned_data['id'])
        except Segment.DoesNotExist:
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
