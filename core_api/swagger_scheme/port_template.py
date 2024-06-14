from drf_yasg import openapi
from core_api.serializers.port_template.port_template_list import PortTemplateListSerializer

port_template_list = {
    'operation_description': 'Get port template list',
    'tags': ['core_api/port_template'],
    'responses': {
        '200': openapi.Response(
            description='Success',
            examples={
                "application/json": {
                    "pagination": {
                        "current_page": 0,
                        "per_page": 0,
                        "next_page": None,
                        "prev_page": None,
                        "total_pages": 0,
                        "total_count": 0
                    },
                    "results": [
                        {
                            "id": 0,
                            "name": "String",
                            "equipment_tmp": {
                                "manufacturer": 'test_1',
                                "model": "test_1"
                            },
                            'count': 0,
                        },
                    ]
                }
            }
        )
    },
    'manual_parameters': [
        openapi.Parameter(name="page",
                          in_=openapi.IN_QUERY,
                          description='Page number',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter(name='per_page',
                          in_=openapi.IN_QUERY,
                          description='Page size',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter(name='order_by',
                          in_=openapi.IN_QUERY,
                          description='Order photo by columns',
                          type=openapi.TYPE_STRING,
                          enum=['-name', '+name', 'count', '-count']),
        openapi.Parameter(name='search_filter',
                          in_=openapi.IN_QUERY,
                          description='Search by symbols',
                          type=openapi.TYPE_STRING),
        openapi.Parameter(name='filter_manufacturer',
                          in_=openapi.IN_QUERY,
                          description='Search by manufacturer',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter(name='filter_model',
                          in_=openapi.IN_QUERY,
                          description='Search by model',
                          type=openapi.TYPE_STRING),
    ]
}

create_port_template = {
    'operation_description': 'Create port template',
    'tags': ['core_api/port_template'],
    'request_body': openapi.Schema(
        title='core_api_create_template',
        description='Create port template',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            name=openapi.Schema(type=openapi.TYPE_STRING),
            count=openapi.Schema(type=openapi.TYPE_INTEGER),
            equipment_tmp_id=openapi.Schema(type=openapi.TYPE_INTEGER),
        ),
        required=['name', 'equipment_tmp_id', 'count']
    ),
    'responses': {201: openapi.Response('Success', PortTemplateListSerializer)}
}

port_temple = {
    'operation_description': 'Get port template',
    'tags': ['core_api/port_template'],
    'responses': {200: openapi.Response('Success', PortTemplateListSerializer)}
}

update_port_template = {
    'operation_description': 'Update port template',
    'tags': ['core_api/port_template'],
    'request_body': openapi.Schema(
        title='core_api_update_port_template',
        description='Update port template',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            name=openapi.Schema(type=openapi.TYPE_STRING),
            count=openapi.Schema(type=openapi.TYPE_INTEGER),
            equipment_tmp_id=openapi.Schema(type=openapi.TYPE_INTEGER),
        ),
    ),
    'responses': {200: openapi.Response('Success', PortTemplateListSerializer)}
}

delete_port_template = {
    'operation_description': 'Delete port template',
    'tags': ['core_api/port_template'],
}
