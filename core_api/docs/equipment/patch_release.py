from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from utils.drf_spectacular_constants.response_for_error import RESPONSE_FOR_ERROR
from utils.types import DocsDict
from core_api.serializers.equipment.list import EquipmentListSerializer

RESPONSES: dict = {
    200: OpenApiResponse(
        description="OK",
        response=EquipmentListSerializer,
        examples=[
            OpenApiExample(
                name="OK",
                value={
                    "id": 1,
                    "template": {
                        "manufacturer": "Cisco",
                        "type": "Switch",
                        "model": "Catalyst 2960",
                        "number_of_units": 1,
                        "count_port": 24,
                        "power": 100
                    },
                    "free_ports": 24,
                    "room": None,
                    "vlan": []
                },
            )
        ],
    ),
    403: OpenApiResponse(
        description="Access is not granted",
        response=RESPONSE_FOR_ERROR,
        examples=[
            OpenApiExample(
                name="Access to the schema not granted",
                value={
                    "type": "ServiceObjectLogicError",
                    "message": "Access to the schema id = 1 is not granted",
                    "translation_key": "invalid",
                    "debug_message": "null",
                    "details": {
                        "current_user": [
                            {
                                "translation_key": "invalid",
                                "message": "Access to the schema id = 1 is not granted",
                            }
                        ]
                    },
                    "additional_info": {},
                    "backtrace": [],
                },
            ),
        ]
    ),
    404: OpenApiResponse(
        description="Not Found",
        response=RESPONSE_FOR_ERROR,
        examples=[
            OpenApiExample(
                name="Not Found",
                value={
                    "type": "ServiceObjectLogicError",
                    "message": "Not found",
                    "translation_key": "not_found",
                    "debug_message": "null",
                    "details": {
                        "id": [
                            {
                                "translation_key": "not_found",
                                "message": "Equipment id=1 not found",
                            }
                        ]
                    },
                    "additional_info": {},
                    "backtrace": [],
                },
            ),
        ],
    ),
}

doc: DocsDict = {
    "tags": ["equipment"],
    "responses": RESPONSES,
}

