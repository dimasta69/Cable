from drf_yasg import openapi
from core_api.serializers.sfp_temaplte.sfp_template import SfpTemplateSerializer

sfp_template_list = {
    'operation_description': "Get sfp template",
    'tags': ['core_api/sfp_template'],
    'responses': {200: openapi.Response('Success', SfpTemplateSerializer)}
}

create_sfp_template = {
    'operation_description': 'Create sfp template',
    'tags': ['core_api/sfp_template'],
    'request_body': openapi.Schema(
        title='core_api_create_sfp_template',
        description='Create sfp template',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            manufacturer_id=openapi.Schema(type=openapi.TYPE_INTEGER),
            speed=openapi.Schema(type=openapi.TYPE_INTEGER),
            name=openapi.Schema(type=openapi.TYPE_STRING),
        ),
        required=['manufacturer_id', 'speed', 'name']
    ),
    'responses': {201: openapi.Response('Success', SfpTemplateSerializer)}
}

sfp_template = {
    'operation_description': 'Get sfp template',
    'tags': ['core_api/sfp_template'],
    'responses': {200: openapi.Response('Success', SfpTemplateSerializer)}
}

delete_sfp_template = {
    'operation_description': 'Delete sfp template',
    'tags': ['core_api/sfp_template']
}

update_sfp_template = {
    'operation_description': 'Update sfp template',
    'tags': ['core_api/sfp_template'],
    'request_body': openapi.Schema(
        title='core_api_sfp_template_update',
        description='Update sfp template',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            name=openapi.Schema(type=openapi.TYPE_STRING),
            speed=openapi.Schema(type=openapi.TYPE_INTEGER),
        ),
    ),
    'responses': {200: openapi.Response('Success', SfpTemplateSerializer)}
}