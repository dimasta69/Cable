from rest_framework import serializers
from models_app.models import PortTemplate, LineType


class SpeedSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    value = serializers.IntegerField(required=True)


class LineTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineType
        fields = (
            "id",
            "name",
        )


class PortTemplateListSerializer(serializers.ModelSerializer):
    speeds = serializers.SerializerMethodField()
    lines_type = serializers.SerializerMethodField()

    def get_speeds(self, obj: PortTemplate) -> SpeedSerializer:
        return SpeedSerializer(obj.speed.all(), many=True).data if obj.speed else None

    def get_lines_type(self, obj: PortTemplate) -> LineTypeSerializer:
        return LineTypeSerializer(obj.line_type.all(), many=True).data if obj.line_type else None

    class Meta:
        model = PortTemplate
        fields = (
            'id',
            'name',
            'type_port',
            'modular',
            'speeds',
            'lines_type',
        )
