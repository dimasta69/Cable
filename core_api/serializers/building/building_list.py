from rest_framework import serializers


class BuildingListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    scheme = serializers.SerializerMethodField()
    number = serializers.CharField(required=True)
    coord_x = serializers.FloatField(required=False)
    coord_y = serializers.FloatField(required=False)

    @classmethod
    def get_scheme(cls, obj):
        return {
            obj.scheme.id
        }
