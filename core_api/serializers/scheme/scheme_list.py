import json

from rest_framework import serializers


class SchemeSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    creator = serializers.SerializerMethodField()
    title = serializers.CharField(required=True)

    class Meta:
        ref_name = 'core_api_scheme_serializer'

    def get_creator(self, obj) -> json:
        return {
            'id': obj.creator.id,
            'username': obj.creator.username,
            'is_superuser': obj.creator.is_superuser
        }
