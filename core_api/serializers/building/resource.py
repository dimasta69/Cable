from rest_framework import serializers

from models_app.models import Building
from typing import Set


class BuildingListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    scheme = serializers.SerializerMethodField()
    name = serializers.CharField(required=True)
    coord_x = serializers.FloatField(required=False)
    coord_y = serializers.FloatField(required=False)
    connection = serializers.ListField(required=False)

    def get_scheme(self, obj: Building) -> Set[str]:
        return {
            obj.scheme.id
        }
