from drf_yasg import openapi

from core_api.serializers.building.building_list import BuildingListSerializer

building_list = {
    'operation_description': 'Get building list',
    'tags': ['core_api/building'],
    'responses': {
        '200': openapi.Response(
            description='Success',
            examples={
                    "results": [
                        {
                            'id': 0,
                            "scheme": 2,
                            'number': 'test',
                            'coord_x': 0.0,
                            'coord_y': 0.0,
                        },
                    ]
            }
        )
    },
    'manual_parameters': [
        openapi.Parameter(name="filter_scheme_id",
                          in_=openapi.IN_QUERY,
                          description='Page number',
                          type=openapi.TYPE_INTEGER,
                          required=True),
    ]
}

create_building = {
    'operation_description': 'Create building',
    'tags': ['core_api/building'],
    'request_body': openapi.Schema(
        title='core_api_create_building',
        description='Create building',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            number=openapi.Schema(type=openapi.TYPE_STRING),
            scheme_id=openapi.Schema(type=openapi.TYPE_INTEGER),
        ),
        required=['number', 'scheme_id']
    ),
    'responses': {201: openapi.Response('Success', BuildingListSerializer)}
}

delete_building = {
    'operation_description': 'Delete building',
    'tags': ['core_api/building']
}

update_building = {
    'operation_description': 'Update building',
    'tags': ['core_api/building'],
    'request_body': openapi.Schema(
        title='core_api_building_update',
        description='Update building',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            number=openapi.Schema(type=openapi.TYPE_STRING),
            coord_x=openapi.Schema(type=openapi.TYPE_STRING),
            coord_y=openapi.Schema(type=openapi.TYPE_STRING),
        ),
    ),
    'responses': {200: openapi.Response('Success', BuildingListSerializer)}
}
