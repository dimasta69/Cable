from drf_yasg import openapi
from core_api.serializers.sfp_template.sfp_template_list import SfpTemplateListSerializer

sfp_template_list = {
    'operation_description': "Get sfp template list",
    'tags': ['core_api/sfp_template'],
    'responses': {200: openapi.Response('Success', SfpTemplateListSerializer)}
}

create_scheme = {
    'operation_description': 'Create scheme',
    'tags': ['core_api/scheme'],
    'request_body': openapi.Schema(
        title='core_api_create_scheme',
        description='Create schema',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            title=openapi.Schema(type=openapi.TYPE_STRING),
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

delete_scheme = {
    'operation_description': 'Delete scheme',
    'tags': ['core_api/scheme']
}

update_scheme = {
    'operation_description': 'Update scheme',
    'tags': ['core_api/scheme'],
    'request_body': openapi.Schema(
        title='core_api_scheme_update',
        description='Update scheme',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            title=openapi.Schema(type=openapi.TYPE_STRING),
        ),
    ),
    'responses': {200: openapi.Response('Success', SfpTemplateListSerializer)}
}
