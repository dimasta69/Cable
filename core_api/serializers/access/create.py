from rest_framework import serializers


class CreateAccessSerializer(serializers.Serializer):
    scheme_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)
    role = serializers.CharField(required=True)
