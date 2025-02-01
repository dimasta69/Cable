from django import forms
from functools import lru_cache

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from typing import List

from utils.services import ServiceWithResult
from utils.fields import ListIntegerField, ModelField
from models_app.models import TypePort, SfpTemplate, Manufacturer, User, LineType, Speed


class CreateSfpTemplateService(ServiceWithResult):
    manufacturer_id = forms.IntegerField(required=True)
    name = forms.CharField(required=False)
    type_port_id = forms.IntegerField(required=False)
    line_type_id = forms.CharField(required=True)
    speeds_id = ListIntegerField()
    current_user = ModelField(User)

    custom_validations = [
        'type_port_presence', 'manufacturer_presence', 'line_type_presence', 'is_superuser', 'speed_presence',
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_sfp_template
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def _create_sfp_template(self):
        return SfpTemplate.objects.create(
            manufacturer=self._manufacturer,
            name=self.cleaned_data['name'],
            type_port=self._type_port,
            line_type=self._line_type,
            speed=self._speeds,
        )

    @property
    @lru_cache()
    def _manufacturer(self):
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['manufacturer_id'])
        except Manufacturer.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _type_port(self):
        try:
            return TypePort.objects.get(id=self.cleaned_data['type_port_id'])
        except TypePort.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _line_type(self) -> LineType | None:
        try:
            return LineType.objects.get(id=self.cleaned_data['line_type_id'])
        except LineType.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _speeds(self) -> List[Speed]:
        try:
            return Speed.objects.filter(id__in=self.cleaned_data['speeds_id'])
        except Speed.DoesNotExist:
            return Speed.objects.none()

    def line_type_presence(self) -> None:
        if self.cleaned_data['line_type_id'] and self._line_type:
            self.add_error(
                "line_type_id",
                ObjectDoesNotExist(
                    f"Line type with id={self.cleaned_data['line_type_id']} not found"
                )
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def speed_presence(self) -> None:
        if len(self._speeds) != len(self.cleaned_data['speeds_id']):
            self.add_error(
                "speeds_id",
                ObjectDoesNotExist(
                    f"Speeds not found"
                )
            )

    def manufacturer_presence(self) -> None:
        if self.cleaned_data['manufacturer_id']:
            if not self._manufacturer:
                self.add_error('filter_manufacturer_id', ObjectDoesNotExist('Manufacturer id='
                                                                            f'{self.cleaned_data["manufacturer_id"]} '
                                                                            f'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def type_port_presence(self) -> None:
        if self.cleaned_data['type_port_id']:
            if not self._type_port:
                self.add_error('filter_type_port_id', ObjectDoesNotExist('Type port id='
                                                                         f'{self.cleaned_data["type_port_id"]} '
                                                                         f'not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied(
                    "User is not superuser"
                )
            )
