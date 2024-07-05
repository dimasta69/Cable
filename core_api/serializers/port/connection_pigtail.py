from rest_framework import serializers


class ConnectionPigtailSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    connection_pigtail_id = serializers.IntegerField(required=True)
