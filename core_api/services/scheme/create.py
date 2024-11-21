from django import forms
from django.core.exceptions import ValidationError
from rest_framework import status
from service_objects.fields import ModelField

from utils.services import ServiceWithResult
from models_app.models.user import User
from models_app.models.scheme import Scheme
from models_app.models.access import Access


class CreateScheme(ServiceWithResult):
    current_user = ModelField(User)
    title = forms.CharField(max_length=100, required=True)

    custom_validations = ['title_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_scheme
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def _create_scheme(self):
        scheme = Scheme.objects.create(creator=self.cleaned_data['current_user'],
                                       title=self.cleaned_data['title'])
        self.create_access(scheme)
        return scheme

    def create_access(self, scheme):
        Access.objects.create(user=self.cleaned_data['current_user'],
                              scheme=scheme,
                              role='Creator')

    @property
    def scheme(self):
        try:
            return Scheme.objects.all()
        except Scheme.DoesNotExist:
            return None

    def title_presence(self):
        for scheme in self.scheme:
            if scheme.title.lower() == self.cleaned_data['title'].lower():
                self.add_error('title', ValidationError("Title="
                                                        f"{self.cleaned_data['title']} already exists"))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
