from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from utils.helpers.auto_parameters_spectacular import prepare_request_body_for_docs
from utils.drf_spectacular_constants.response_for_error import RESPONSE_FOR_ERROR
from utils.types import DocsDict
from core_api.serializers.scheme.resource import SchemeSerializer
from core_api.services.scheme.create import CreateScheme

RESPONSES: dict = {
    201: OpenApiResponse(
        description="Created",
        response=SchemeSerializer,
        examples=[
            OpenApiExample(
                name="Created",
                value={
                    "id": 1,
                    "creator": {
                        "id": 1,
                        "username": "root",
                        "is_superuser": True
                    },
                    "title": "New Scheme",
                    "count_user": 1,
                    "count_build": 0
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
}

doc: DocsDict = {
    "tags": ["scheme"],
    "request": prepare_request_body_for_docs(CreateScheme, exclude=("current_user",)),
    "responses": RESPONSES,
}

