from rest_framework import serializers
from core_api.serializers.equipment.equipment import EquipmentSerializer


class RoomListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    number = serializers.CharField(required=True)
    is_server_room = serializers.BooleanField(required=True)
    equipments = EquipmentSerializer(many=True, required=False)
    floor = serializers.IntegerField(required=False)
