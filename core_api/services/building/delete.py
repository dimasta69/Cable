from functools import lru_cache

from django import forms
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status

from models_app.models import Access, User
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models.building import Building


class DeleteBuildingService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['building_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.delete_building
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    @property
    def delete_building(self):
        self.building.delete()
        return None

    @property
    @lru_cache()
    def building(self):
        try:
            return Building.objects.get(id=self.cleaned_data['id'])
        except Building.DoesNotExist:
            return None

    @property
    def access(self):
        try:
            return Access.objects.get(user=self.cleaned_data['current_user'], scheme=self.building.scheme,
                                      role__in=['Change', 'Creator'])
        except Access.DoesNotExist:
            return None

    def building_presence(self):
        if not self.building:
            self.add_error('id', ObjectDoesNotExist('Building id='
                                                    f'{self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self):
        if self.building:
            if not self.access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.building.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
