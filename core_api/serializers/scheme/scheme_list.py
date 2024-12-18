import json

from rest_framework import serializers
from models_app.models import Scheme


class SchemeSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()

    def get_creator(self, obj: Scheme) -> json:
        return {
            'id': obj.creator.id,
            'username': obj.creator.username,
            'is_superuser': obj.creator.is_superuser
        }

    class Meta:
        model = Scheme
        fields = (
            'id',
            'creator'
            "title",
            "count_user",
            "count_build",
        )
