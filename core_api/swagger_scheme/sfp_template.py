from drf_yasg import openapi
from core_api.serializers.sfp_template.sfp_template_list import SfpTemplateListSerializer
from core_api.serializers.equipment.equipment import EquipmentSerializer

sfp_template_list = {
    'operation_description': "Get sfp template list",
    'tags': ['core_api/sfp_template'],
    'responses': {200: openapi.Response('Success', SfpTemplateListSerializer)}
}

create_sfp_template = {
    'operation_description': 'Create scheme',
    'tags': ['core_api/sfp_template'],
    'request_body': openapi.Schema(
        title='core_api_create_scheme',
        description='Create schema',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            manufacturer_id=openapi.Schema(type=openapi.TYPE_INTEGER),
            name=openapi.Schema(type=openapi.TYPE_STRING),
            type_port_id=openapi.Schema(type=openapi.TYPE_INTEGER),
            line_type=openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['Одномодовый', 'Многомодовый', 'Медный провод', 'None']
            ),
            speed=openapi.Schema(type=openapi.TYPE_ARRAY,
                                 items=openapi.Schema(type=openapi.TYPE_INTEGER)),
        ),
        required=['title']
    ),
    'responses': {201: openapi.Response('Success', SfpTemplateListSerializer)}
}

scheme = {
    'operation_description': 'Get scheme',
    'tags': ['core_api/scheme'],
    'responses': {200: openapi.Response('Success', SfpTemplateListSerializer)}
}

delete_sfp_template = {
    'operation_description': 'Delete sfp template',
    'tags': ['core_api/sfp_template']
}

adding_to_ports = {
    'operation_description': 'Adding to ports sfp template',
    'tags': ['core_api/sfp_template'],
    'request_body': openapi.Schema(
        title='core_api_adding_to_ports',
        description='Adding to ports sfp template',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            title=openapi.Schema(type=openapi.TYPE_STRING),
            port_list=openapi.Schema(type=openapi.TYPE_ARRAY,
                                     items=openapi.Schema(type=openapi.TYPE_INTEGER)),
            equipment_id=openapi.Schema(type=openapi.TYPE_INTEGER),

        ),
    ),
    'responses': {200: openapi.Response('Success', SfpTemplateListSerializer)}
}
