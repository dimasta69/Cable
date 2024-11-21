from rest_framework import serializers


class DisconnectPortListSerializer(serializers.Serializer):
    port_list = serializers.ListField(required=True)
    equipment_id = serializers.IntegerField(required=True)
