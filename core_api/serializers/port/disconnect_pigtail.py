from rest_framework import serializers


class DisconnectPigtail(serializers.Serializer):
    pigtail_list = serializers.ListField(required=True)
    equipment_id = serializers.IntegerField(required=True)
