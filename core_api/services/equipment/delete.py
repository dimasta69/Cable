from django import forms
from functools import lru_cache
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.equipment import Equipment
from models_app.models.server_rack import ServerRack
from models_app.models.port import Port


class DeleteEquipmentService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    server_rack_id = forms.IntegerField(required=False)

    custom_validations = ['equipment_presence', 'server_rack_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.delete_equipment
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    @property
    def delete_equipment(self):
        self.port_list.delete()
        self.equipment.delete()
        if self.cleaned_data['server_rack_id']:
            self.server_rack.check_free_power()
        return None

    @property
    @lru_cache()
    def equipment(self):
        try:
            return Equipment.objects.get(id=self.cleaned_data['id'])
        except Equipment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def server_rack(self):
        try:
            return ServerRack.objects.get(id=self.cleaned_data['server_rack_id'])
        except ServerRack.DoesNotExist:
            return None

    @property
    @lru_cache()
    def port_list(self):
        try:
            return Port.objects.filter(equipment=self.equipment)
        except Port.DoesNotExist:
            return Port.objects.none()

    def equipment_presence(self):
        if not self.equipment:
            self.add_error('id', ObjectDoesNotExist(f'Equipment id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def server_rack_presence(self):
        if self.cleaned_data['server_rack_id']:
            if not self.server_rack:
                self.add_error('server_rack_id', ObjectDoesNotExist('Server rack id='
                                                                    f'{self.cleaned_data["server_rack_id"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND
