from rest_framework import serializers

from models_app.models import SchemeMap


class MapListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemeMap
        fields = (
            'id',
            'name',
        )
