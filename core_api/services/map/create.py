from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from functools import lru_cache

from utils.services import ServiceWithResult
from models_app.models import User, Access, Scheme, SchemeMap
from utils.fields import ModelField


class CreateMapService(ServiceWithResult):
    name = forms.CharField(required=True)
    scheme_id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['access_presence', 'scheme_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_scheme_map
        return self

    @property
    def _create_scheme_map(self) -> SchemeMap:
        return SchemeMap.objects.create(
            name=self.cleaned_data['name'],
            scheme=self._scheme,
        )

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data['scheme_id'])
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

    def access_presence(self) -> None:
        if self.cleaned_data['scheme_id']:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.cleaned_data["scheme_id"]} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN

    def scheme_presence(self) -> None:
        if not self._scheme:
            self.add_error('id', ObjectDoesNotExist('Scheme id='
                                                    f'{self.cleaned_data["scheme_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND
