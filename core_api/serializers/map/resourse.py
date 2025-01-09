from rest_framework import serializers

from models_app.models import SchemeMap
from core_api.serializers.equipment.equipment import EquipmentSerializer


class MapSerializer(serializers.ModelSerializer):
    equipments = serializers.ModelSerializer()

    def get_equipments(self, obj: SchemeMap):
        return EquipmentSerializer(obj.scheme.equipments, many=True).data

    class Meta:
        model = SchemeMap
        fields = (
            "id",
            "name",
            "equipments",
        )
