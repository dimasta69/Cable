from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from utils.helpers.auto_parameters_spectacular import prepare_request_body_for_docs
from utils.drf_spectacular_constants.response_for_error import RESPONSE_FOR_ERROR
from utils.types import DocsDict
from core_api.serializers.scheme.resource import SchemeSerializer
from core_api.services.scheme.update import SchemeUpdateService

RESPONSES: dict = {
    200: OpenApiResponse(
        description="OK",
        response=SchemeSerializer,
        examples=[
            OpenApiExample(
                name="OK",
                value={
                    "id": 1,
                    "creator": {
                        "id": 1,
                        "username": "root",
                        "is_superuser": True
                    },
                    "title": "Updated Scheme",
                    "count_user": 5,
                    "count_build": 3
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
                        "title": [
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
                    "message": "Access to the schema is not granted",
                    "translation_key": "invalid",
                    "debug_message": "null",
                    "details": {
                        "current_user": [
                            {
                                "translation_key": "invalid",
                                "message": "User access not allowed. Only the creator or administrator has access to update",
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
                                "message": "Scheme id = 1 not found",
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
    "tags": ["scheme"],
    "request": prepare_request_body_for_docs(SchemeUpdateService, exclude=("current_user", "id")),
    "responses": RESPONSES,
}

