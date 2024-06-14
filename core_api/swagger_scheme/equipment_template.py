from drf_yasg import openapi

from core_api.serializers.equipment_template.equipment_template import EquipmentTemplateSerializer

equipment_template_list = {
    'operation_description': 'Get equipment template list',
    'tags': ['core_api/equipment_template'],
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
                            "manufacturer": {
                                "id": 0,
                                "name": "test_1"
                            },
                            'type': 'test',
                            'model': 'test'
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
                          description='Order equipment template by columns',
                          type=openapi.TYPE_STRING,
                          enum=['power', '-power', 'number_of_units', '-number_of_units', 'count_port', '-count_port']),
        openapi.Parameter(name='search_filter',
                          in_=openapi.IN_QUERY,
                          description='Search by symbols',
                          type=openapi.TYPE_STRING),
        openapi.Parameter(name='filter_type',
                          in_=openapi.IN_QUERY,
                          description='Search by type',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter(name='filter_manufacturer',
                          in_=openapi.IN_QUERY,
                          description='Search by manufacturer',
                          type=openapi.TYPE_STRING),
    ]
}

create_equipment_template = {
    'operation_description': 'Create equipment template',
    'tags': ['core_api/equipment_template'],
    'request_body': openapi.Schema(
        title='core_api_create_equipment_template',
        description='Create equipment template',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            manufacturer_id=openapi.Schema(type=openapi.TYPE_INTEGER),
            type=openapi.Schema(type=openapi.TYPE_STRING),
            model=openapi.Schema(type=openapi.TYPE_STRING),
            number_of_units=openapi.Schema(type=openapi.TYPE_INTEGER),
            power=openapi.Schema(type=openapi.TYPE_INTEGER),
        ),
        required=['type', 'model']
    ),
    'responses': {201: openapi.Response('Success', EquipmentTemplateSerializer)}
}

equipment_template = {
    'operation_description': 'Get equipment template',
    'tags': ['core_api/equipment_template'],
    'responses': {200: openapi.Response('Success', EquipmentTemplateSerializer)}
}

delete_equipment_template = {
    'operation_description': 'Delete equipment template',
    'tags': ['core_api/equipment_template']
}

update_equipment_template = {
    'operation_description': 'Update equipment template',
    'tags': ['core_api/equipment_template'],
    'request_body': openapi.Schema(
        title='core_api_equipment_template_update',
        description='Update manufacturer',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            manufacturer_id=openapi.Schema(type=openapi.TYPE_INTEGER),
            type=openapi.Schema(type=openapi.TYPE_STRING),
            model=openapi.Schema(type=openapi.TYPE_STRING),
            number_of_units=openapi.Schema(type=openapi.TYPE_INTEGER),
            power=openapi.Schema(type=openapi.TYPE_INTEGER),
        ),
    ),
    'responses': {200: openapi.Response('Success', EquipmentTemplateSerializer)}
}