from django import forms
from rest_framework import status
from rest_framework.exceptions import NotFound
from functools import lru_cache

from utils.services import ServiceWithResult
from models_app.models import Segment


class UpdateSegmentService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    name = forms.CharField(required=True)

    custom_validations = ["segment_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_segment()
        return self

    def _update_segment(self) -> Segment:
        segment = self._segment
        segment.name = self.cleaned_data['name']
        segment.save()
        return segment

    @property
    @lru_cache()
    def _segment(self) -> Segment | None:
        try:
            return Segment.objects.get(id=self.cleaned_data['id'])
        except Segment.DoesNotExist:
            return None

    def segment_presence(self) -> None:
        self.add_error(
            "id",
            NotFound(
                f"Segment id={self.cleaned_data['id']} not found"
            )
        )
        self.response_status = status.HTTP_404_NOT_FOUND
