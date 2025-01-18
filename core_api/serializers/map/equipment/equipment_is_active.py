from rest_framework import serializers

from models_app.models import EquipmentSchemeIsActive


class EquipmentIsActiveMapSerializer(serializers.ModelSerializer):
    equipment_id = serializers.IntegerField(source="equipment.id")

    class Meta:
        model = EquipmentSchemeIsActive
        fields = (
            "id",
            "equipment_id",
            "coord_x",
            "coord_y",
            "connection_active",
            "connection_passive",
        )
