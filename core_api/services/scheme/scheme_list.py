from service_objects.fields import ModelField
from rest_framework import status
from django import forms

from models_app.models import User
from models_app.models import Scheme
from models_app.models import Access
from utils.services import ServiceWithResult


class SchemeListService(ServiceWithResult):
    current_user = ModelField(User)
    search_filter = forms.CharField(required=False)

    def process(self):
        if self.is_valid():
            self.result = self._filter_list
            self.response_status = status.HTTP_200_OK
        return self

    def _filter_list(self):
        scheme_list = self.scheme_list
        if self.cleaned_data.get('search_filter'):
            scheme_list = scheme_list.filter(scheme__title__icontains=self.cleaned_data["search_filter"])
        return scheme_list

    @property
    def scheme_list(self):
        try:
            return Scheme.objects.filter(id__in=self.scheme_to_access).select_related('creator')
        except Scheme.DoesNotExist:
            return Scheme.objects.none()

    @property
    def scheme_to_access(self):
        try:
            return (Access.objects.filter(user=self.cleaned_data['current_user'])
                    .select_related('scheme').values_list('scheme', flat=True))
        except Access.DoesNotExist:
            return []
