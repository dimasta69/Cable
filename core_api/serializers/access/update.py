from rest_framework import  serializers


class UpdateAccessSerializer(serializers.Serializer):
    role = serializers.CharField(required=True)
