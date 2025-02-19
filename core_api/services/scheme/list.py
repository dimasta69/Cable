from django.contrib.contenttypes.models import ContentType
from service_objects.fields import ModelField
from rest_framework import status
from django import forms
from functools import lru_cache
from typing import List

from models_app.models import User
from models_app.models import Scheme
from models_app.models import Access
from utils.services import ServiceWithResult


class SchemeListService(ServiceWithResult):
    current_user = ModelField(User)
    search_filter = forms.CharField(required=False)

    # scheme_content_type = ContentType.objects.get_for_model(Scheme)

    def process(self):
        if self.is_valid():
            self.result = self._filter_list
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _filter_list(self) -> List[Scheme]:
        scheme_list = self._scheme_list
        if self.cleaned_data.get('search_filter'):
            scheme_list = scheme_list.filter(title__icontains=self.cleaned_data["search_filter"])
        return scheme_list.order_by("created_at")

    @property
    @lru_cache()
    def _scheme_list(self) -> List[Scheme]:
        try:
            return Scheme.objects.filter(id__in=self.scheme_to_access).select_related('creator')
        except Scheme.DoesNotExist:
            return Scheme.objects.none()

    @property
    def scheme_to_access(self) -> Access | list[None]:
        try:
            return Access.objects.filter(
                user=self.cleaned_data['current_user'],
                # object_type=self.scheme_content_type,
            ).values_list('object_id', flat=True)
        except Access.DoesNotExist:
            return []
