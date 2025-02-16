from core_api.services.equipment.list import EquipmentListService
from typing import List
from models_app.models import Equipment, Vlan, VlanDevice
from django.db.models import Q


class EquipmentFromSearchService(EquipmentListService):
    @property
    def _equipment_filter_list(self) -> List[Equipment]:
        equipment_list = self._equipment_list
        if self.cleaned_data['filter_segment_id']:
            equipment_list = equipment_list.filter(
                id__in=Vlan.objects.filter(
                    segment=self._segment, device__device_type=self.equipment_content_type
                ).values_list("device__device_id", flat=True)
            )
        if self.cleaned_data['filter_vlan_list_id']:
            equipment_list = equipment_list.filter(
                id__in=self._vlan.filter(
                    device__device_type=self.equipment_content_type
                ).values_list("device__device_id", flat=True)
            )
        if self.cleaned_data['filter_manufacturer_id']:
            equipment_list = equipment_list.filter(template__manufacturer=self._manufacturer)
        if self.cleaned_data['filter_type_id']:
            equipment_list = equipment_list.filter(template__type=self._type)
        if self.cleaned_data['filter_scheme_id']:
            equipment_list = equipment_list.filter(scheme=self._scheme).distinct()
        if self.cleaned_data['filter_server_rack_id']:
            equipment_list = equipment_list.filter(unit__server_rack=self._server_rack).distinct()
        if self.cleaned_data['filter_room_id']:
            equipment_list = equipment_list.filter(room=self._room)
        if self.cleaned_data['search_filter']:
            equipment_list = equipment_list.filter(
                Q(template__model__icontains=self.cleaned_data['search_filter']) |
                Q(template__manufacturer__name__icontains=self.cleaned_data['search_filter']) |
                Q(id__in=VlanDevice.objects.filter(vlan__segment__scheme=self._scheme).filter(
                    Q(ip__icontains=self.cleaned_data['search_filter'])
                    ).values_list('device_id', flat=True))
            )
        if self.cleaned_data['order_by']:
            equipment_list = equipment_list.order_by(self.cleaned_data['order_by'])
        return equipment_list
