from rest_framework import serializers

from models_app.models import EquipmentTemplateType


class EquipmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentTemplateType
        fields = (
            "name",
            "is_active",
        )
