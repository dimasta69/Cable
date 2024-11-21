from drf_yasg import openapi
from core_api.serializers.type_port.type_port_list import TypePortListSerializer

type_port_list = {
    'operation_description': "Get type port list",
    'tags': ['core_api/type_port'],
    'responses': {200: openapi.Response('Success', TypePortListSerializer)}
}
