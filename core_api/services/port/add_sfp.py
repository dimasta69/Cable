from django import forms
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from models_app.models.sfp_template import SfpTemplate
from models_app.models.port import Port


class AddSfpService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    sfp_template_id = forms.IntegerField(required=True)

    custom_validations = ['port_presence', 'sfp_presence', 'speed_matching', 'modular']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.add_sfp
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def add_sfp(self):
        port = self.port
        if not port.sfp:
            port.sfp = self.sfp
        else:
            if port.connection:
                port.connection.connection = None
                port.connection.line_type = None
                port.connection = None
                port.line_type = None
                port.sfp = self.sfp
        port.save()
        return self.port_list

    @property
    @lru_cache()
    def port(self):
        try:
            return Port.objects.get(id=self.cleaned_data['id'])
        except Port.DoesNotExist:
            return None

    @property
    @lru_cache()
    def sfp(self):
        try:
            return SfpTemplate.objects.get(id=self.cleaned_data['sfp_template_id'])
        except SfpTemplate.DoesNotExist:
            return None

    @property
    def port_list(self):
        try:
            return Port.objects.filter(equipment=self.port.equipment)
        except Port.DoesNotExist:
            return Port.objects.none()

    def port_presence(self):
        if not self.port:
            self.add_error('id', ObjectDoesNotExist(f"Port id = {self.cleaned_data['id']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def sfp_presence(self):
        if not self.sfp:
            self.add_error('sfp_template_id', ObjectDoesNotExist("Sfp template id = "
                                                                 f"{self.cleaned_data['sfp_template_id']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def speed_matching(self):
        if self.sfp and self.port:
            sfp_speed = set(self.sfp.speed)
            port_speed = set(self.port.port_template.speed)
            if not sfp_speed.intersection(port_speed):
                self.add_error('id', SuspiciousOperation('Speed mismatch'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def modular(self):
        if self.port:
            if not self.port.port_template.modular:
                self.add_error('id', SuspiciousOperation('Port is not modular'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
