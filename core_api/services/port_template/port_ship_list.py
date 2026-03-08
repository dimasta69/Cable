from django import forms
from functools import lru_cache
from django.core.exceptions import ObjectDoesNotExist

from core_api.utils.presence import PresenceChecksMixin
from utils.services import ServiceWithResult
from models_app.models import Equipment, PortShip


class PortShipListService(PresenceChecksMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)

    custom_validations = ["run_presence_checks", "port_ship_presence"]
    presence_checks = [("_equipment", "id", "Equipment")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._port_ship
        return self

    @property
    @lru_cache()
    def _equipment(self):
        try:
            return Equipment.objects.get(id=self.cleaned_data['id'])
        except Equipment.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _port_ship(self):
        try:
            return PortShip.objects.filter(equipment_template=self._equipment.template)
        except PortShip.DoesNotExist:
            return PortShip.objects.none()

    def port_ship_presence(self):
        if not self._port_ship:
            self.add_error(
                "id",
                ObjectDoesNotExist(
                    f"Port ship with equipment template id={self.cleaned_data['id']} does not exist"
                )
            )
