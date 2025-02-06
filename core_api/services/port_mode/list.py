from django import forms
from typing import List

from utils.services import ServiceWithResult
from models_app.models import PortMode


class PortModeListService(ServiceWithResult):
    filter_is_only_vlan = forms.BooleanField(required=False)

    def process(self):
        if self.is_valid():
            self.result = self._port_mode
        return self


    @property
    def _port_mode(self) -> List[PortMode]:
        try:
            return PortMode.objects.all()
        except PortMode.DoesNotExist:
            return PortModeList.objects.none()

