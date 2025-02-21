from rest_framework import serializers
from models_app.models.port.port_template.models import PortShip
from models_app.models import EquipmentTemplate
from typing import Union, Dict


class EquipmentTemplateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    manufacturer = serializers.SerializerMethodField(required=False)
    type = serializers.SerializerMethodField(required=False)
    model = serializers.CharField(required=True)
    number_of_units = serializers.IntegerField(required=False)
    power = serializers.IntegerField(required=False)
    count_port = serializers.SerializerMethodField()

    def get_manufacturer(self, obj: EquipmentTemplate) -> Dict[str, Union[int, str]]:
        if obj.manufacturer:
            return {
                'id': obj.manufacturer.id,
                'name': obj.manufacturer.name,
            }
        else:
            return None

    def get_type(self, obj: EquipmentTemplate) -> Dict[str, Union[int, bool, str]]:
        return {
            "id": obj.type.id,
            "is_active": obj.type.is_active,
            "name": obj.type.name,
        }

    def get_count_port(self, obj: EquipmentTemplate) ->  int:
        return sum(PortShip.objects.filter(equipment_template=obj).values_list('count', flat=True))
