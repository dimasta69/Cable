from rest_framework import serializers


class ConnectionPigtailListSerializer(serializers.Serializer):
    pigtail_list = serializers.ListField(required=True)
    connection_pigtail_list = serializers.ListField(required=True)
    equipment_id = serializers.IntegerField(required=True)
    connection_equipment_id = serializers.IntegerField(required=True)
