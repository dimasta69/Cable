from rest_framework import serializers


class CreateEquipmentSerializer(serializers.Serializer):
    equipment_template_id = serializers.IntegerField(required=True)
    vlan_ip = serializers.JSONField(required=False)
    unit_list_id = serializers.ListField()
    server_rack_id = serializers.IntegerField()
