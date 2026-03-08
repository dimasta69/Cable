from django import forms
from django.core.exceptions import ObjectDoesNotExist
from functools import lru_cache
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from typing import List

from core_api.utils.presence import PresenceChecksMixin
from utils.services import ServiceWithResult
from utils.fields import ListIntegerField, ModelField
from models_app.models import TypePort, SfpTemplate, Manufacturer, User, LineType, Speed, Port


class UpdateSfpTemplateService(PresenceChecksMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    manufacturer_id = forms.IntegerField(required=False)
    name = forms.CharField(required=False)
    type_port_id = forms.IntegerField(required=False)
    line_type_id = ListIntegerField(required=False)
    speeds_id = ListIntegerField(required=False)
    current_user = ModelField(User)

    custom_validations = [
        'run_presence_checks', 'line_type_presence', 'speed_presence',
        'is_superuser', 'template_not_used_by_ports',
    ]
    presence_checks = [
        ("_sfp_template", "id", "Sfp template"),
        ("_manufacturer", "manufacturer_id", "Manufacturer", True),
        ("_type_port", "type_port_id", "Type port", True),
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_sfp_template
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _update_sfp_template(self) -> SfpTemplate:
        template = self._sfp_template
        if self.cleaned_data.get('manufacturer_id'):
            template.manufacturer = self._manufacturer
        if self.cleaned_data.get('name') is not None:
            template.name = self.cleaned_data['name']
        if self.cleaned_data.get('type_port_id'):
            template.type_port = self._type_port
        template.save()
        if isinstance(self.cleaned_data.get('line_type_id'), list):
            template.line_type.set(self._line_type)
        if isinstance(self.cleaned_data.get('speeds_id'), list):
            template.speed.set(self._speeds)
        return SfpTemplate.objects.get(pk=template.pk)

    @property
    @lru_cache()
    def _sfp_template(self) -> SfpTemplate | None:
        try:
            return SfpTemplate.objects.get(id=self.cleaned_data['id'])
        except SfpTemplate.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _manufacturer(self) -> Manufacturer | None:
        if not self.cleaned_data.get('manufacturer_id'):
            return None
        try:
            return Manufacturer.objects.get(id=self.cleaned_data['manufacturer_id'])
        except Manufacturer.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _type_port(self) -> TypePort | None:
        if not self.cleaned_data.get('type_port_id'):
            return None
        try:
            return TypePort.objects.get(id=self.cleaned_data['type_port_id'])
        except TypePort.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _line_type(self) -> List[LineType]:
        if not self.cleaned_data.get('line_type_id'):
            return []
        return list(LineType.objects.filter(id__in=self.cleaned_data['line_type_id']))

    @property
    @lru_cache()
    def _speeds(self) -> List[Speed]:
        if not self.cleaned_data.get('speeds_id'):
            return []
        return list(Speed.objects.filter(id__in=self.cleaned_data['speeds_id']))

    def line_type_presence(self) -> None:
        if not self.cleaned_data.get('line_type_id'):
            return
        if len(self._line_type) != len(self.cleaned_data['line_type_id']):
            self.add_error(
                "line_type_id",
                ObjectDoesNotExist("Line type with id=%s not found" % self.cleaned_data['line_type_id']),
            )
            self.response_status = status.HTTP_404_NOT_FOUND

    def speed_presence(self) -> None:
        if not self.cleaned_data.get('speeds_id'):
            return
        if len(self._speeds) != len(self.cleaned_data['speeds_id']):
            self.add_error("speeds_id", ObjectDoesNotExist("Speeds not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def template_not_used_by_ports(self) -> None:
        if not self._sfp_template:
            return
        if Port.objects.filter(sfp_id=self._sfp_template.pk).exists():
            self.add_error(
                "id",
                ObjectDoesNotExist(
                    "Невозможно изменить шаблон SFP: существуют порты, использующие этот шаблон."
                ),
            )
            self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def is_superuser(self) -> None:
        if not self.cleaned_data['current_user'].is_superuser:
            self.add_error(
                "current_user",
                PermissionDenied("User is not superuser"),
            )
            self.response_status = status.HTTP_403_FORBIDDEN
