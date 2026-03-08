from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from utils.helpers.auto_parameters_spectacular import prepare_request_body_for_docs
from utils.drf_spectacular_constants.response_for_error import RESPONSE_FOR_ERROR
from utils.types import DocsDict
from core_api.serializers.building.resource import BuildingListSerializer
from core_api.services.building.create import CreateBuildingService

RESPONSES: dict = {
    201: OpenApiResponse(
        description="Created",
        response=BuildingListSerializer,
        examples=[
            OpenApiExample(
                name="Created",
                value={
                    "id": 1,
                    "scheme_id": 1,
                    "name": "Building A",
                    "coord_x": None,
                    "coord_y": None,
                    "connection": []
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
                        "scheme_id": [
                            {
                                "translation_key": "required",
                                "message": "This field is required."
                            }
                        ],
                        "name": [
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
    422: OpenApiResponse(
        description="Unprocessable Entity",
        response=RESPONSE_FOR_ERROR,
        examples=[
            OpenApiExample(
                name="Building name already exists",
                value={
                    "type": "ServiceObjectLogicError",
                    "message": "Field with number=Building A already exists",
                    "translation_key": "invalid",
                    "debug_message": "null",
                    "details": {
                        "number": [
                            {
                                "translation_key": "invalid",
                                "message": "Field with number=Building A already exists",
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
    "tags": ["building"],
    "request": prepare_request_body_for_docs(CreateBuildingService, exclude=("current_user",)),
    "responses": RESPONSES,
}

