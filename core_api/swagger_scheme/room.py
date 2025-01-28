from drf_yasg import openapi

from core_api.serializers.room.resource import RoomListSerializer

room_list = {
    'operation_description': 'Get room list',
    'tags': ['core_api/room'],
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
                            'number': 'test',
                            'type': ' Серверная',
                            'count_free_socket': 0,
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
                          description='Order by columns',
                          type=openapi.TYPE_STRING,
                          enum=['number', '-number']),
        openapi.Parameter(name='filter_type',
                          in_=openapi.IN_QUERY,
                          description='Filter by type',
                          type=openapi.TYPE_STRING,
                          enum=['Серверная', 'Обычная']),
        openapi.Parameter(name='filter_building_id',
                          in_=openapi.IN_QUERY,
                          description='Filter by building id',
                          type=openapi.TYPE_INTEGER,
                          required=True),
        openapi.Parameter(name='search_filter',
                          in_=openapi.IN_QUERY,
                          description='Search by symbols',
                          type=openapi.TYPE_STRING),
    ]
}

create_room = {
    'operation_description': 'Create room',
    'tags': ['core_api/room'],
    'request_body': openapi.Schema(
        title='core_api_crate_room',
        description='Create room',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            building_id=openapi.Schema(type=openapi.TYPE_INTEGER),
            number=openapi.Schema(type=openapi.TYPE_STRING),
            type=openapi.Schema(type=openapi.TYPE_STRING),
        ),
        required=['type', 'building_id', 'number']
    ),
    'responses': {201: openapi.Response('Success', RoomListSerializer)},
    'manual_parameters': [
            openapi.Parameter(name='type',
                              in_=openapi.IN_QUERY,
                              description='Type equipment template',
                              type=openapi.TYPE_STRING,
                              enum=['Серверная', 'Обычная']),
        ]
}

delete_room = {
    'operation_description': 'Delete room',
    'tags': ['core_api/room']
}

update_room = {
    'operation_description': 'Update room',
    'tags': ['core_api/room'],
    'request_body': openapi.Schema(
        title='core_api_room_update',
        description='Update room',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            id=openapi.Schema(type=openapi.TYPE_INTEGER),
            number=openapi.Schema(type=openapi.TYPE_STRING),
        ),
        required=['id'],
    ),
    'responses': {200: openapi.Response('Success', RoomListSerializer)}
}
