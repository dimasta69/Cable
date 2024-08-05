from django import forms
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from utils.fields import ListIntegerField
from models_app.models.port import Port
from models_app.models.equipment import Equipment


class DisconnectPigtailService(ServiceWithResult):
    pigtail_list = ListIntegerField(required=True)
    equipment_id = forms.IntegerField(required=True)

    custom_validations = ['equipment_presence', 'pigtail_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.disconnect_pigtail
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def disconnect_pigtail(self):
        for pigtail in self.pigtail_list_dict:
            pigtail.connection_pigtail = None
            pigtail.connection_pigtail.connection_pigtail = None
            pigtail.save()
        return self.pigtail_list_int.order_by('uid')

    @property
    @lru_cache()
    def pigtail_list_int(self):
        try:
            return Port.objects.filter(equipment=self.equipment)
        except Port.DoesNotExist:
            return Port.objects.none()

    @property
    @lru_cache()
    def pigtail_list_dict(self):
        connection_pigtail_list_dict = []
        for uid in self.cleaned_data['pigtail_list']:
            try:
                connection_pigtail_list_dict.append(self.pigtail_list_int.get(id=uid))
            except Port.DoesNotExist:
                return None
        return connection_pigtail_list_dict

    @property
    @lru_cache()
    def equipment(self):
        try:
            return Equipment.objects.get(id=self.cleaned_data['equipment_id'])
        except Equipment.DoesNotExist:
            return None

    def equipment_presence(self):
        if not self.equipment:
            self.add_error('id', ObjectDoesNotExist(f"Equipment id ={self.cleaned_data['equipment_id']} not found"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def pigtail_presence(self):
        if not self.pigtail_list_dict:
            self.add_error('id', ObjectDoesNotExist("Pigtail not found"))
            self.response_status = status.HTTP_404_NOT_FOUND
