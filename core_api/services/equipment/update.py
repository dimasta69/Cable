from django import forms
from functools import lru_cache
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from utils.services import ServiceWithResult
from utils.fields import JsonIpField
from models_app.models.equipment import Equipment
from models_app.models.room import Room


class UpdateEquipmentService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    vlan_ip = JsonIpField(required=False)
    room_id = forms.IntegerField(required=False)

    custom_validations = ['equipment_presence', 'room_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.update_equipment
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def update_equipment(self):
        equipment = self.equipment
        if self.cleaned_data['vlan_ip']:
            equipment.vlan_ip = self.cleaned_data['vlan_ip']
        if self.cleaned_data['room_id']:
            equipment.room = self.room
            equipment.save()
        return equipment

    @property
    @lru_cache()
    def equipment(self):
        try:
            return Equipment.objects.get(id=self.cleaned_data['id'])
        except Equipment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def room(self):
        try:
            return Room.objects.get(id=self.cleaned_data['room_id'])
        except Room.DoesNotExist:
            return None

    def equipment_presence(self):
        if not self.equipment:
            self.add_error('id', ObjectDoesNotExist(f'Equipment id={self.cleaned_data["id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def room_presence(self):
        if self.cleaned_data['room_id']:
            if not self.room:
                self.add_error('room_id', ObjectDoesNotExist(f'Room id= {self.cleaned_data["room_id"]} not found'))
                self.response_status = status.HTTP_404_NOT_FOUND