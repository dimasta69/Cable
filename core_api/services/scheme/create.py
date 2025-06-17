from django import forms
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from service_objects.fields import ModelField
from django.db import transaction

from utils.services import ServiceWithResult
from models_app.models import User
from models_app.models import Scheme
from models_app.models import Access


class CreateScheme(ServiceWithResult):
    current_user = ModelField(User)
    title = forms.CharField(max_length=100, required=True)

    def process(self):
        if self.is_valid():
            with transaction.atomic():
                scheme = self._create_scheme
                self._create_access(scheme)
                self.result = scheme
                self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def _create_scheme(self):
        scheme = Scheme.objects.create(
            creator=self.cleaned_data['current_user'],
            title=self.cleaned_data['title'],
        )
        return scheme

    def _create_access(self, scheme: Scheme) -> None:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        Access.objects.create(
            user=self.cleaned_data['current_user'],
            role='Creator',
            object_type=scheme_content_type,
            object_id=scheme.pk,
        )
