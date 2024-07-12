from rest_framework import serializers


class UpdateEquipmentSerializer(serializers.Serializer):
    vlan_ip = serializers.JSONField(required=False)
