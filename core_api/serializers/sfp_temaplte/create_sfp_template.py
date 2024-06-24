from rest_framework import serializers


class CreateSfpTemplateSerializer(serializers.Serializer):
    manufacturer_id = serializers.IntegerField(required=True)
    speed = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    line_type = serializers.CharField(required=False)

    class Meta:
        ref_name = 'core_api_create_sfp_template_serializer'
