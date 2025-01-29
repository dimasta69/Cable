from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from typing import List

from utils.services import ServiceWithResult
from django import forms
from functools import lru_cache
from models_app.models import User
from utils.fields import ModelField
from models_app.models import Scheme
from models_app.models import Access
from django.db.models import Q


class UsersListServices(ServiceWithResult):
    page = forms.IntegerField(required=False)
    current_user = ModelField(User)
    per_page = forms.IntegerField(required=False)
    search_filter = forms.CharField(required=False)
    order_by = forms.CharField(required=False)
    scheme_id = forms.IntegerField(required=True)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)

    custom_validations = ['scheme_presence', 'order_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._scheme_list_filter
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _scheme_list_filter(self) -> List[User]:
        user_list = self._users
        if self.cleaned_data['order_by']:
            user_list = user_list.order_by(self.cleaned_data['order_by'])
        if self.cleaned_data['search_filter']:
            user_list = user_list.filter(
                Q(username__icontains=self.cleaned_data['search_filter'])
            )
        return user_list

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.get(id=self.cleaned_data['scheme_id'])
        except Scheme.DoesNotExist:
            return None

    @property
    def _users(self) -> List[User]:
        try:
            return User.objects.exclude(id__in=self._access)
        except User.DoesNotExist:
            return User.objects.none()

    @property
    def _access(self) -> List[Access]:
        try:
            return Access.objects.filter(
                object_type=self.scheme_content_type,
                object_id=self._scheme.pk,
            ).values_list('user__id', flat=True)
        except Access.DoesNotExist:
            return Access.objects.none()

    def scheme_presence(self) -> None:
        if not self._scheme:
            self.add_error('scheme_id', ObjectDoesNotExist('Scheme id='
                                                           f'{self.cleaned_data["scheme_id"]} '
                                                           'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def order_presence(self) -> None:
        if self.cleaned_data['order_by']:
            if not self.cleaned_data['order_by'] in ['username', '-username']:
                self.add_error('order_by', ObjectDoesNotExist(f'Order {self.cleaned_data["order_by"]} is not found'))
                self.response_status = status.HTTP_404_NOT_FOUND
