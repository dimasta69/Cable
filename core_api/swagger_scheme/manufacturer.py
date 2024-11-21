from drf_yasg import openapi
from core_api.serializers.manufacturer.manufacturer_list import ManufacturerListSerializer


manufacturer_list = {
    'operation_description': "Get manufacturers",
    'tags': ['core_api/manufacturer'],
    'responses': {200: openapi.Response('Success', ManufacturerListSerializer)}
}

create_manufacturer = {
    'operation_description': 'Create manufacturer',
    'tags': ['core_api/manufacturer'],
    'request_body': openapi.Schema(
        title='core_api_create_manufacturer',
        description='Create manufacturer',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            name=openapi.Schema(type=openapi.TYPE_STRING),
        ),
        required=['name']
    ),
    'responses': {201: openapi.Response('Success', ManufacturerListSerializer)}
}

manufacturer = {
    'operation_description': 'Get manufacturer',
    'tags': ['core_api/manufacturer'],
    'responses': {200: openapi.Response('Success', ManufacturerListSerializer)}
}

delete_manufacturer = {
    'operation_description': 'Delete manufacturer',
    'tags': ['core_api/manufacturer']
}

update_manufacturer = {
    'operation_description': 'Update manufacturer',
    'tags': ['core_api/manufacturer'],
    'request_body': openapi.Schema(
        title='core_api_manufacturer_update',
        description='Update manufacturer',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            name=openapi.Schema(type=openapi.TYPE_STRING),
        ),
    ),
    'responses': {200: openapi.Response('Success', ManufacturerListSerializer)}
}
