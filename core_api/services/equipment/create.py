from django import forms
from django.core.exceptions import ObjectDoesNotExist
from functools import lru_cache

from rest_framework import status

from utils.services import ServiceWithResult
from utils.fields import JsonIpField
from models_app.models.equipment import Equipment
from models_app.models.equipment_template import EquipmentTemplate
from models_app.models.port import Port
from models_app.models.port_template import PortTemplate
from models_app.models.room import Room


class CreateEquipmentService(ServiceWithResult):
    equipment_template_id = forms.IntegerField(required=True)
    vlan_ip = JsonIpField(required=False)
    room_id = forms.IntegerField(required=False)

    custom_validations = ['equipment_template_presence', 'port_template_presence', 'room_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.create_equipment
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def create_equipment(self):
        equipment = Equipment.objects.create(template=self.equipment_template, vlan_ip=self.cleaned_data['vlan_ip'],
                                             room=self.room)
        number = 1
        for port_template in self.port_template_list:
            for port in range(port_template.count):
                Port.objects.create(uid=number, equipment=equipment, port_template=port_template)
                number += 1

        equipment.set_free_ports()
        return equipment

    @property
    @lru_cache()
    def equipment_template(self):
        try:
            return EquipmentTemplate.objects.get(id=self.cleaned_data['equipment_template_id'])
        except EquipmentTemplate.DoesNotExist:
            return None

    @property
    @lru_cache()
    def port_template_list(self):
        try:
            return PortTemplate.objects.filter(equipment_tmp=self.equipment_template)
        except PortTemplate.DoesNotExist:
            return PortTemplate.objects.none()

    @property
    @lru_cache()
    def room(self):
        try:
            return Room.objects.get(id=self.cleaned_data['room_id'])
        except Room.DoesNotExist:
            return None

    def equipment_template_presence(self):
        if not self.equipment_template:
            self.add_error('equipment_template_id', ObjectDoesNotExist('Equipment template id='
                                                                       f'{self.cleaned_data["equipment_template_id"]}'
                                                                       ' not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def port_template_presence(self):
        if not self.port_template_list:
            self.add_error('port_template_list', ObjectDoesNotExist('Port template where equipment template id='
                                                                    f'{self.cleaned_data["equipment_template_id"]}'
                                                                    ' not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def room_presence(self):
        if self.cleaned_data['room_id']:
            if not self.room:
                self.add_error('room_id', ObjectDoesNotExist(f'Room id= {self.cleaned_data["room_id"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND
