from rest_framework import serializers


class DisconnectSfpSerializer(serializers.Serializer):
    port_list = serializers.ListField(required=True)
