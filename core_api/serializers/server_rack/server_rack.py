from rest_framework import serializers

from models_app.models import Unit


class ServerRackSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    number_of_units = serializers.IntegerField(required=True)
    title = serializers.CharField(required=False)
    max_power = serializers.IntegerField(required=False)
    free_power = serializers.IntegerField(required=False)
    free_units = serializers.IntegerField(required=False)
    units = serializers.SerializerMethodField()

    def get_units(self, obj):
        units = []
        for unit in Unit.objects.filter(server_rack=obj).order_by('uid').select_related(
                'equipment', 'equipment__template', 'equipment__template__manufacturer'):
            if unit.equipment:
                equipment_data = {
                    'id': unit.equipment.id,
                    'equipment_id': unit.equipment.template.id,
                    'manufacturer': unit.equipment.template.manufacturer.name,
                    'type': unit.equipment.template.type,
                    'model': unit.equipment.template.model
                }
            else:
                equipment_data = None

            unit_data = {
                'id': unit.id,
                'uid': unit.uid,
                'side': unit.side,
                'equipment': equipment_data
            }
            units.append(unit_data)

        return units
