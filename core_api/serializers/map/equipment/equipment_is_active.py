from rest_framework import serializers

from models_app.models import EquipmentScheme


class EquipmentIsActiveMapSerializer(serializers.ModelSerializer):
    equipment_id = serializers.IntegerField(source="equipment.id")

    class Meta:
        model = EquipmentScheme
        fields = (
            "id",
            "equipment_id",
            "coord_x",
            "coord_y",
            "connection_active",
            "connection_passive",
        )
