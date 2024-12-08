from django import forms
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from functools import lru_cache

from rest_framework import status

from models_app.models import Access, User
from utils.services import ServiceWithResult
from utils.fields import JsonIpField, ModelField
from models_app.models import Equipment
from models_app.models import EquipmentTemplate
from models_app.models import Port
from models_app.models import PortTemplate
from models_app.models import Room


class CreateEquipmentFromRoomService(ServiceWithResult):
    equipment_template_id = forms.IntegerField(required=True)
    vlan_ip = JsonIpField(required=False)
    room_id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['equipment_template_presence', 'port_template_presence', 'room_presence',
                          'room_type', 'access_presence']

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
    def room(self):
        try:
            return Room.objects.get(id=self.cleaned_data['room_id'])
        except Room.DoesNotExist:
            return None

    @property
    @lru_cache()
    def port_template_list(self):
        try:
            return PortTemplate.objects.filter(equipment_tmp=self.equipment_template)
        except PortTemplate.DoesNotExist:
            return PortTemplate.objects.none()

    @property
    def access(self):
        try:
            return Access.objects.get(user=self.cleaned_data['current_user'], scheme=self.room.building.scheme,
                                      role__in=['Change', 'Creator'])
        except Access.DoesNotExist:
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
        if not self.room:
            self.add_error('room_id', ObjectDoesNotExist(f'Room id={self.cleaned_data["room_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def room_type(self):
        if self.room:
            if self.room.type != 'Обычная':
                self.add_error('room_id', ObjectDoesNotExist('Еhe type of room should be ordinary'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def access_presence(self):
        if self.room:
            if not self.access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.room.building.scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN
