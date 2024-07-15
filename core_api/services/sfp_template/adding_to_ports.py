from django import forms
from functools import lru_cache

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from utils.services import ServiceWithResult
from utils.fields import ListIntegerField
from models_app.models.port import Port
from models_app.models.sfp_template import SfpTemplate


class AddToPortSfpService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    port_list = ListIntegerField(required=True)

    custom_validations = ['port_list_dict_presence', 'sfp_template_presence']

    @property
    def add_sfp(self):
        for port in self.port_list_dict:
            port.sfp = self.sfp_template

    @property
    def port_list(self):
        try:
            return Port.objects.all()
        except Port.DoesNotExist:
            return Port.objects.none()

    @property
    def sfp_template(self):
        try:
            return SfpTemplate.objects.all()
        except SfpTemplate.DoesNotExist:
            return None

    @property
    @lru_cache()
    def port_list_dict(self):
        port_list_dict = []
        for uid in self.cleaned_data['port_list']:
            try:
                port_list_dict.append(self.port_list.get(id=uid))
            except Port.DoesNotExist:
                return None
        return port_list_dict

    def port_list_dict_presence(self):
        if self.cleaned_data['port_list']:
            if not self.port_list_dict:
                self.add_error('port_list', ObjectDoesNotExist('Port list id='
                                                               f'{self.cleaned_data["port_list"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def sfp_template_presence(self):
        if self.cleaned_data['id']:
            if not self.port_list_dict:
                self.add_error('id', ObjectDoesNotExist('Sfp template id='
                                                        f'{self.cleaned_data["id"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def sfp_coincidence_port(self):
        if self.port_list_dict and self.sfp_template:
            for port in self.port_list_dict:
                if not port.port_template.modular or not set(port.port_template.speed).intersection(set(self.sfp_template.speed)):
