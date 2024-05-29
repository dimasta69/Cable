from drf_yasg import openapi
from core_api.serializers.scheme.scheme_list import SchemeSerializer

scheme_list = {
    'operation_description': "Get schemes",
    'tags': ['core_api/scheme'],
    'responses': {200: openapi.Response('Success', SchemeSerializer)}
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
    'responses': {201: openapi.Response('Success', SchemeSerializer)}
}

scheme = {
    'operation_description': 'Get scheme',
    'tags': ['core_api/scheme'],
    'responses': {200: openapi.Response('Success', SchemeSerializer)}
}
