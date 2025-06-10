from rest_framework import serializers

from models_app.models import Figure


class FigureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Figure
        fields = (
            'id',
            'title',
            'x',
            'y',
            'width',
            'height',
            'type',
        )
 