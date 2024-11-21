from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from rest_framework import status

from cabel.settings import REST_FRAMEWORK
from utils.services import ServiceWithResult
from django import forms
from functools import lru_cache
from models_app.models.user import User
from utils.fields import ModelField
from models_app.models.scheme import Scheme
from models_app.models.access import Access
from django.db.models import Q


class UsersListServices(ServiceWithResult):
    page = forms.IntegerField(required=False)
    current_user = ModelField(User)
    per_page = forms.IntegerField(required=False)
    search_filter = forms.CharField(required=False)
    order_by = forms.CharField(required=False)
    scheme_id = forms.IntegerField(required=True)

    custom_validations = ['scheme_presence', 'order_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._scheme_list_filter()
            self.response_status = status.HTTP_200_OK
        return self

    def _scheme_list_filter(self):
        user_list = self._users
        if self.cleaned_data['order_by']:
            user_list = user_list.order_by(self.cleaned_data['order_by'])
        if self.cleaned_data['search_filter']:
            user_list = user_list.filter(
                Q(username_icontains=self.cleaned_data['search_filter'])
            )
        try:
            return (Paginator(user_list, per_page=(self.cleaned_data['per_page'] or
                                                   REST_FRAMEWORK['PAGE_SIZE'])).
                    page(self.cleaned_data['page'] or 1))
        except EmptyPage:
            return (Paginator(user_list, per_page=(self.cleaned_data['per_page'] or
                                                   REST_FRAMEWORK['PAGE_SIZE'])).page(1))

    @property
    @lru_cache()
    def _scheme(self):
        try:
            return Scheme.objects.get(id=self.cleaned_data['scheme_id'])
        except Scheme.DoesNotExist:
            return None

    @property
    def _users(self):
        try:
            return User.objects.exclude(id__in=self._access)
        except User.DoesNotExist:
            return User.objects.none()

    @property
    def _access(self):
        try:
            return Access.objects.filter(scheme=self._scheme).values_list('user__id', flat=True)
        except Access.DoesNotExist:
            return Access.objects.none()

    def scheme_presence(self):
        if not self._scheme:
            self.add_error('scheme_id', ObjectDoesNotExist('Scheme id='
                                                           f'{self.cleaned_data["scheme_id"]} '
                                                           'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def order_presence(self):
        if self.cleaned_data['order_by']:
            if not self.cleaned_data['order_by'] in ['username', '-username']:
                self.add_error('order_by', ObjectDoesNotExist(f'Order {self.cleaned_data["order_by"]} is not found'))
                self.response_status = status.HTTP_404_NOT_FOUND
