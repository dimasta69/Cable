from django import forms
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from utils.fields import ListIntegerField
from models_app.models.port import Port
from models_app.models.equipment import Equipment


class ConnectionPigtailListService(ServiceWithResult):
    pigtail_list = ListIntegerField(required=True)
    connection_pigtail_list = ListIntegerField(required=True)
    equipment_id = forms.IntegerField(required=True)
    connection_equipment_id = forms.IntegerField(required=True)

    custom_validations = ['equipment_presence', 'connection_equipment_presence', 'port_connection_presence',
                          'port_presence', 'equipment_type_presence', 'pigtail_already', 'connection_pigtail_already',
                          'sum_pigtail', 'correspondence_pigtail_list', 'correspondence_connection_pigtail_list']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.connection_pigtail_port
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def connection_pigtail_port(self):
        for pigtail, connection_pigtail in zip(self.pigtail_list_dict, self.connection_pigtail_list_dict):
            pigtail.set_connection_pigtail(connection_pigtail)
        return self.equipment

    @property
    @lru_cache()
    def port_list_int(self):
        try:
            return Port.objects.all()
        except Port.DoesNotExist:
            return Port.objects.none()

    @property
    @lru_cache()
    def connection_pigtail_list_dict(self):
        connection_pigtail_list_dict = []
        for uid in self.cleaned_data['connection_pigtail_list']:
            try:
                connection_pigtail_list_dict.append(self.port_list_int.get(id=uid))
            except Port.DoesNotExist:
                return None
        return sorted(connection_pigtail_list_dict, key=lambda port: port.uid)

    @property
    @lru_cache()
    def pigtail_list_dict(self):
        pigtail_list_dict = []
        for uid in self.cleaned_data['pigtail_list']:
            try:
                pigtail_list_dict.append(self.port_list_int.get(id=uid))
            except Port.DoesNotExist:
                return None
        return sorted(pigtail_list_dict, key=lambda port: port.uid)

    @property
    @lru_cache()
    def equipment(self):
        try:
            return Equipment.objects.get(id=self.cleaned_data['equipment_id'])
        except Equipment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def connection_equipment(self):
        try:
            return Equipment.objects.get(id=self.cleaned_data['connection_equipment_id'])
        except Equipment.DoesNotExist:
            return None

    def equipment_presence(self):
        if not self.equipment:
            self.add_error('id', ObjectDoesNotExist(f"Equipment id ={self.cleaned_data['equipment_id']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def connection_equipment_presence(self):
        if not self.connection_equipment:
            self.add_error('id', ObjectDoesNotExist(f"Equipment id ={self.cleaned_data['connection_equipment_id']}"
                                                    " not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def port_connection_presence(self):
        if self.cleaned_data['connection_pigtail_list']:
            if not self.connection_pigtail_list_dict:
                self.add_error('pigtail_list', ObjectDoesNotExist('Pigtail list does not exist'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def port_presence(self):
        if self.cleaned_data['pigtail_list']:
            if not self.pigtail_list_dict:
                self.add_error('pigtail_list', ObjectDoesNotExist('Pigtail list does not exist'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def equipment_type_presence(self):
        if self.connection_equipment and self.equipment:
            if (self.connection_equipment.template.type != 'Пассивное оборудование' or self.equipment.template.type
                    != 'Пассивное оборудование'):
                self.add_error('equipment_id', SuspiciousOperation('The equipment is not a patch panel'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def pigtail_already(self):
        if self.pigtail_list_dict:
            pigtail_list = [pigtail for pigtail in self.pigtail_list_dict if pigtail.connection_pigtail is not None]
            if pigtail_list:
                self.add_error('pigtail_list',  SuspiciousOperation('Pigtail is already connected'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def connection_pigtail_already(self):
        if self.connection_pigtail_list_dict:
            connection_pigtail_list =\
                [pigtail for pigtail in self.connection_pigtail_list_dict if pigtail.connection_pigtail is not None]
            if connection_pigtail_list:
                self.add_error('pigtail_list', SuspiciousOperation('Pigtail is already connected'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def sum_pigtail(self):
        if self.connection_pigtail_list_dict and self.pigtail_list_dict:
            count_pigtail = len(self.pigtail_list_dict)
            count_connection_pigtail = len(self.connection_pigtail_list_dict)
            if count_pigtail != count_connection_pigtail:
                self.add_error('pigtail_list', SuspiciousOperation("The number of ports is not suitable."
                                                                   f"{count_pigtail} != {count_connection_pigtail}"))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def correspondence_pigtail_list(self):
        if self.pigtail_list_dict:
            filtered_pigtails = [pigtail for pigtail in self.pigtail_list_dict if pigtail.equipment == self.equipment]
            if len(filtered_pigtails) != len(self.pigtail_list_dict):
                self.add_error('pigtail_list', SuspiciousOperation("Not all ports comply with the specified "
                                                                   "equipment"))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def correspondence_connection_pigtail_list(self):
        if self.connection_pigtail_list_dict:
            filtered_pigtails = [pigtail for pigtail in self.connection_pigtail_list_dict if pigtail.equipment ==
                                 self.connection_equipment]
            if len(filtered_pigtails) != len(self.connection_pigtail_list_dict):
                self.add_error('connection_pigtail_list', SuspiciousOperation("Not all ports comply with the"
                                                                              " specified equipment"))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
