from django import forms
from functools import lru_cache
from django.core.exceptions import ObjectDoesNotExist

from utils.services import ServiceWithResult
from models_app.models import EquipmentTemplate, PortShip


class PortShipListService(ServiceWithResult):
    id = forms.IntegerField(required=True)

    custom_validations = ["equipment_template_presence", "port_ship_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._port_ship
        return self

    @property
    @lru_cache()
    def _equipment_template(self):
        try:
            return EquipmentTemplate.objects.get(id=self.cleaned_data['id'])
        except EquipmentTemplate.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _port_ship(self):
        try:
            return PortShip.objects.filter(eqipment_template=self._equipment_template)
        except PortShip.DoesNotExist:
            return PortShip.objects.none()

    def equipment_template_presence(self):
        if not self._equipment_template:
            self.add_error(
                "id",
                ObjectDoesNotExist(
                    f"Equipment template with id={self.cleaned_data['id']} does not exist"
                )
            )

    def port_ship_presence(self):
        if not self._port_ship:
            self.add_error(
                "id",
                ObjectDoesNotExist(
                    f"Port ship with equipment template id={self.cleaned_data['id']} does not exist"
                )
            )
