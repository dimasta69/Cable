from rest_framework import serializers

from models_app.models import EquipmentScheme
from core_api.serializers.equipment.list import EquipmentListSerializer


class EquipmentIsActiveMapSerializer(serializers.ModelSerializer):
    equipment = EquipmentListSerializer()

    class Meta:
        model = EquipmentScheme
        fields = (
            "id",
            "equipment",
            "coord_x",
            "coord_y",
            "connection_active",
            "connection_passive",
        )
