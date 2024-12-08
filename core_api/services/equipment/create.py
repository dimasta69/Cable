from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from functools import lru_cache

from rest_framework import status

from models_app.models import Unit
from utils.services import ServiceWithResult
from utils.fields import JsonIpField
from utils.fields import ListIntegerField
from models_app.models import Equipment
from models_app.models import EquipmentTemplate
from models_app.models import Port
from models_app.models import PortTemplate
from models_app.models import ServerRack


class CreateEquipmentService(ServiceWithResult):
    equipment_template_id = forms.IntegerField(required=True)
    vlan_ip = JsonIpField(required=False)
    unit_list_id = ListIntegerField(required=True)
    server_rack_id = forms.IntegerField(required=True)

    custom_validations = ['equipment_template_presence', 'port_template_presence',
                          'unit_free_presence', 'count_unit_presence', 'unit_list_presence', 'server_rack_presence',
                          'server_rack_correspond_presence', 'power_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.create_equipment
            self.response_status = status.HTTP_201_CREATED
        return self

    @property
    def create_equipment(self):
        equipment = Equipment.objects.create(template=self.equipment_template, vlan_ip=self.cleaned_data['vlan_ip'])
        number = 0
        objects_to_create = []

        for port_template in self.port_template_list:
            for i in range(port_template.count):
                number = number + 1
                objects_to_create.append(Port(uid=number, equipment=equipment, port_template=port_template))
        Port.objects.bulk_create(objects_to_create)
        equipment.free_ports = equipment.count_port
        self.add_equipment(equipment)
        return self.server_rack

    def add_equipment(self, equipment):
        self.unit_list_int.all().update(equipment=equipment)
        self.server_rack.check_free_power()
        self.server_rack.check_free_units()

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
            return (PortTemplate.objects.filter(equipment_tmp=self.equipment_template).order_by('unit', 'id')
                    .select_related('equipment_tmp'))
        except PortTemplate.DoesNotExist:
            return PortTemplate.objects.none()

    @property
    @lru_cache()
    def server_rack(self):
        try:
            return ServerRack.objects.get(id=self.cleaned_data['server_rack_id'])
        except ServerRack.DoesNotExist:
            return None

    @property
    @lru_cache()
    def unit_list_int(self):
        unit_list = Unit.objects.filter(id__in=self.cleaned_data['unit_list_id']).select_related('server_rack')
        if unit_list.count() < len(self.cleaned_data['unit_list_id']):
            return Unit.objects.none()
        return unit_list

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

    def unit_list_presence(self):
        if self.cleaned_data['unit_list_id']:
            if not self.unit_list_int:
                self.add_error('unit_list_id', ObjectDoesNotExist('Unit list id='
                                                                  f'{self.cleaned_data["unit_list_id"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def count_unit_presence(self):
        if self.cleaned_data['unit_list_id']:
            if self.unit_list_int and self.equipment_template:
                if not len(self.unit_list_int) == self.equipment_template.number_of_units:
                    self.add_error('unit_list_id', ValidationError('Quantities units do not match'))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def unit_free_presence(self):
        if self.cleaned_data['unit_list_id']:
            if self.unit_list_int and self.equipment_template:
                if self.unit_list_int.filter(equipment__isnull=False):
                    self.add_error('unit_list_id', ValidationError('Not all units are free'))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def server_rack_presence(self):
        if not self.server_rack:
            self.add_error('server_rack_id', ObjectDoesNotExist('Server rack id= '
                                                                f'{self.cleaned_data["server_rack_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def server_rack_correspond_presence(self):
        if self.server_rack and self.unit_list_int:
            for unit in self.unit_list_int:
                if unit.server_rack.id != self.server_rack.id:
                    self.add_error('unit_list_id', ValidationError('Server rack do not correspond unit with id='
                                                                   f'{unit.id}'))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def power_presence(self):
        if self.server_rack and self.equipment_template:
            if self.server_rack.free_power and self.equipment_template.power:
                if self.server_rack.free_power < self.equipment_template.power:
                    self.add_error('server_rack_id', ValidationError('Not enough freer power = '
                                                                     f'{self.server_rack.free_power}'))
                    self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
