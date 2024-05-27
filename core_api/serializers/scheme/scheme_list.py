from rest_framework import serializers

from models_app.models.user import User


class SchemeSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    creator = serializers.PrimaryKeyRelatedField(queryset=User)
    title = serializers.CharField(required=True)

    class Meta:
        ref_name = 'core_api_scheme_serializer'
