from rest_framework import serializers


class CreateFromRoomEquipmentSerializer(serializers.Serializer):
    equipment_template_id = serializers.IntegerField(required=True)
    vlan_ip = serializers.JSONField(required=False)
    room_id = serializers.IntegerField(required=True)
