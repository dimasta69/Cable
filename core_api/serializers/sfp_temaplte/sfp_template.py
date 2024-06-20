from rest_framework import serializers


class SfpTemplateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    manufacturer = serializers.SerializerMethodField()
    speed = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)

    class Meta:
        ref_name = 'core_api_sfp_template_serializer'

    @classmethod
    def get_manufacturer(cls, obj):
        return {
            obj.manufacturer.name
        }
