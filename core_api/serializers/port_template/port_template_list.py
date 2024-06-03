from rest_framework import serializers


class PortTemplateListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)

    class Meta:
        ref = 'core_api_port_template_list_serializer'
