from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from utils.helpers.auto_parameters_spectacular import prepare_request_body_for_docs
from utils.drf_spectacular_constants.response_for_error import RESPONSE_FOR_ERROR
from utils.types import DocsDict
from core_api.serializers.equipment.list import EquipmentListSerializer
from core_api.services.equipment.create import CreateEquipmentService

RESPONSES: dict = {
    201: OpenApiResponse(
        description="Created",
        response=EquipmentListSerializer,
        examples=[
            OpenApiExample(
                name="Created",
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
    400: OpenApiResponse(
        description="Bad Request",
        response=RESPONSE_FOR_ERROR,
        examples=[
            OpenApiExample(
                name="Bad Request (not all parameters have been passed)",
                description="Bad Request because not all parameters have been passed",
                value={
                    "type": "InvalidInputsError",
                    "message": "Invalid request data",
                    "translation_key": "invalid_request_data",
                    "debug_message": "null",
                    "details": {
                        "equipment_template_id": [
                            {
                                "translation_key": "required",
                                "message": "This field is required."
                            }
                        ],
                        "scheme_id": [
                            {
                                "translation_key": "required",
                                "message": "This field is required."
                            }
                        ],
                    },
                    "additional_info": {},
                    "backtrace": [],
                },
            ),
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
                        "equipment_template_id": [
                            {
                                "translation_key": "not_found",
                                "message": "Equipment template id=1 not found",
                            }
                        ],
                        "scheme_id": [
                            {
                                "translation_key": "not_found",
                                "message": "Scheme id=1 not found",
                            }
                        ],
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
    "request": prepare_request_body_for_docs(CreateEquipmentService, exclude=("current_user",)),
    "responses": RESPONSES,
}

