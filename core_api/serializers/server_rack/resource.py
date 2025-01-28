from rest_framework import serializers

from models_app.models import Unit

class EquipmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    manufacturer = serializers.CharField(source="manufacturer.name")
    type = serializers.CharField(source="template.type")
    model = serializers.CharField(source="template.model")

class UnitSerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer(allow_null=True)

    class Meta:
        model = Unit
        fields = (
            "id",
            "uid",
            "side",
            "equipment",
        )


class ServerRackSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    number_of_units = serializers.IntegerField(required=True)
    title = serializers.CharField(required=False)
    max_power = serializers.IntegerField(required=False)
    free_power = serializers.IntegerField(required=False)
    free_units = serializers.IntegerField(required=False)
    units = serializers.SerializerMethodField()

    def get_units(self, obj):
        units = Unit.objects.filter(server_rack=obj).order_by('uid').select_related(
            'equipment', 'equipment__template', 'equipment__template__manufacturer'
        )

        return UnitSerializer(units, many=True).data
