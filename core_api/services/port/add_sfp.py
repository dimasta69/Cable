from django import forms
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.sfp_template import SfpTemplate
from models_app.models.port import Port


class AddSfpService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    sfp_template_id = forms.IntegerField(required=True)

    custom_validations = ['port_presence', 'sfp_presence', 'speed_matching']

    @property
    def add_sfp(self):
        if not self.port.sfp:
            self.port.sfp = self.sfp

    @property
    def port(self):
        try:
            return Port.objects.get(id=self.cleaned_data['id'])
        except Port.DoesNotExist:
            return None

    @property
    def sfp(self):
        try:
            return SfpTemplate.objects.get(id=self.cleaned_data['sfp_template_id'])
        except SfpTemplate.DoesNotExist:
            return None

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
