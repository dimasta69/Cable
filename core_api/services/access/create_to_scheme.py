from django import forms
from functools import lru_cache

from django.core.exceptions import PermissionDenied
from rest_framework import status
from django.contrib.contenttypes.models import ContentType

from core_api.utils.presence import PresenceChecksMixin
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Scheme
from models_app.models import User
from models_app.models import Access


class CreateAccessService(PresenceChecksMixin, ServiceWithResult):
    scheme_id = forms.IntegerField(required=True)
    user_id = forms.IntegerField(required=True)
    role = forms.CharField(required=True)
    current_user = ModelField(User)

    custom_validations = ['run_presence_checks', 'role_presence', 'access_owner_or_superuser']
    presence_checks = [
        ("_scheme", "scheme_id", "Scheme"),
        ("_user", "user_id", "User"),
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_access
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def _create_access(self) -> Access:
        scheme_content_type = ContentType.objects.get_for_model(Scheme)
        return Access.objects.create(
            user=self._user,
            role=self.cleaned_data['role'],
            object_type=scheme_content_type,
            object_id=self.cleaned_data['scheme_id'],
        )

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data['scheme_id'])
        except Scheme.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _user(self) -> User | None:
        try:
            return User.objects.get(id=self.cleaned_data['user_id'])
        except User.DoesNotExist:
            return None

    def role_presence(self) -> None:
        if self.cleaned_data['role']:
            if self.cleaned_data.get('role') not in Access.ASSIGNABLE_ROLE_VALUES:
                self.add_error('filter_role', ObjectDoesNotExist(f"Field in model with "
                                                                 f"{self.cleaned_data['role']} not found"))
                self.response_status = status.HTTP_404_NOT_FOUND

    def access_owner_or_superuser(self) -> None:
        if self._scheme and self._user:
            if (self._scheme.creator != self.cleaned_data['current_user']
                    and not self.cleaned_data['current_user'].is_superuser):
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._scheme.pk} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
