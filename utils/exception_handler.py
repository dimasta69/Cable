import sys
import traceback

from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from utils import errors as exceptions
from .errors import InvalidInputsError
from .errors import ServiceObjectLogicError


def custom_exception_handler(
    exception: (
        Exception
        | MultipleObjectsReturned
        | ObjectDoesNotExist
        | Http404
        | drf_exceptions.NotAuthenticated
        | drf_exceptions.AuthenticationFailed
        | drf_exceptions.PermissionDenied
        | drf_exceptions.ParseError
        | drf_exceptions.ValidationError
        | InvalidInputsError
        | ServiceObjectLogicError
    ),
) -> (
    exceptions.NotFound
    | exceptions.ValidationError
    | MultipleObjectsReturned
    | exceptions.AuthenticationFailed
    | exceptions.AccessDenied
    | ServiceObjectLogicError
):
    """
    Method which transform different exceptions to the same form and same signature.
    :param exception:
    """
    # handle Django exceptions
    if isinstance(exception, Http404):
        exception = exceptions.NotFound()
    elif isinstance(exception, ObjectDoesNotExist):
        if " matching query does not exist." in exception.__str__():  # Main case for ObjectDoesNotExist
            model_name = exception.__str__().split(" matching query does not exist.")[0]
            details = {
                model_name.lower(): [
                    {
                        "translation_key": "object_not_found",
                        "message": exception.__str__(),
                    }
                ]
            }
            exception = exceptions.NotFound(details=details)
        elif " has no " in exception.__str__():  # RelatedObjectDoesNotExist case
            model_name, field_name = exception.__str__().split(" has no ")
            details = {
                field_name[:-1]: [
                    {
                        "translation_key": "related_object_not_found",
                        "message": exception.__str__(),
                    }
                ]
            }
            exception = exceptions.ValidationError(details=details)
    elif isinstance(exception, MultipleObjectsReturned):
        debug_message = exception.__str__()
        exception = exceptions.Error()
        exception.debug_message = debug_message
    elif isinstance(exception, drf_exceptions.NotAuthenticated):
        exception = exceptions.AuthenticationFailed(details=str(exception))
    elif isinstance(exception, drf_exceptions.AuthenticationFailed):
        exception.translation_key = exception.detail.code
        exception.message = str(exception)
        exception = exceptions.AuthenticationFailed(
            message=str(exception),
            translation_key=exception.detail.code,
            debug_message="Signature has expired.",
        )
    elif isinstance(exception, drf_exceptions.PermissionDenied):
        debug_message = exception.__str__()
        exception = exceptions.AccessDenied()
        exception.debug_message = debug_message
    elif isinstance(exception, drf_exceptions.ParseError):
        pass
    elif isinstance(exception, drf_exceptions.ValidationError):
        details = {}
        if isinstance(exception, drf_exceptions.AuthenticationFailed):
            if hasattr(exception, "response_status"):
                exception = exceptions.ValidationError(
                    message=str(exception.detail[0]),
                    response_status=exception.response_status,
                )
            else:
                exception = exceptions.ValidationError(message=str(exception.detail[0]))
        else:
            for field, exception_details in exception.get_full_details().items():
                details[field] = [
                    {
                        "translation_key": exception_detail.get("code"),
                        "message": exception_detail.get("message").capitalize(),
                    }
                    for exception_detail in exception_details
                ]
            if hasattr(exception, "response_status"):
                exception = exceptions.ValidationError(details=details, response_status=exception.response_status)
            else:
                exception = exceptions.ValidationError(details=details)
    # handle ServiceObjects library  exceptions
    elif isinstance(exception, InvalidInputsError):
        details = {}
        for field, exception_details in exception.errors.items():
            detail_list = []
            for exception_detail in exception_details:
                for detail in exception_detail.error_list:
                    for message in detail.messages:
                        detail_list.append({"translation_key": detail.code, "message": message})
            details[field] = detail_list
        exception = exceptions.ValidationError(details=details)
    elif isinstance(exception, ServiceObjectLogicError):
        errors_list = [item for sublist in exception.errors_dict.values() for item in sublist]
        if exception.response_status == getattr(exception, "_default_response_status"):
            for error in errors_list:
                if hasattr(error, "response_status") and (error.response_status > exception.response_status):
                    exception.response_status = error.response_status
                    if hasattr(error, "message"):
                        exception.message = error.message
                    if hasattr(error, "translation_key"):
                        exception.translation_key = error.translation_key
        details = {}
        for field, exception_details in exception.errors_dict.items():
            detail_list = []
            for exception_detail in exception_details:
                if hasattr(exception_detail, "translation_key"):
                    translation_key = exception_detail.translation_key
                else:
                    translation_key = "invalid"
                if hasattr(exception_detail, "message"):
                    message = exception_detail.message
                else:
                    message = exception_detail.__str__()
                detail_list.append(
                    {
                        "translation_key": translation_key,
                        "message": message,
                    }
                )
            details[field] = detail_list
        exception.details = details
    return exception


def drf_exception_response(
    exception: (
        Exception
        | MultipleObjectsReturned
        | ObjectDoesNotExist
        | Http404
        | drf_exceptions.NotAuthenticated
        | drf_exceptions.AuthenticationFailed
        | drf_exceptions.PermissionDenied
        | drf_exceptions.ParseError
        | drf_exceptions.ValidationError
        | InvalidInputsError
        | ServiceObjectLogicError
    ),
    context,
) -> Response:
    """
    Django middleware to catch exceptions and change them using new structure with extra fields.
    :param exception:
    :param context:
    """
    exception = custom_exception_handler(exception)
    extend_exception_for_response(exception)
    return Response(exception.response_dict, status=exception.response_status)


def extend_exception_for_response(exception):
    """
    Method which add new extra fields to exception and then return it.
    :param exception:
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    translation_key = exception.translation_key if hasattr(exception, "translation_key") else "internal_server_error"
    debug_message = exception.debug_message if hasattr(exception, "debug_message") else exc_value.__str__()
    details = exception.details if hasattr(exception, "details") else None
    additional_info = exception.additional_info if hasattr(exception, "additional_info") else None
    try:
        response_status = exception.response_status
    except AttributeError:
        response_status = 500
    try:
        message = exception.message
    except AttributeError:
        message = "We are sorry but something went wrong"

    error_dict = {
        "type": exc_type.__name__,
        "message": message,
        "translation_key": translation_key,
        "debug_message": debug_message,
        "backtrace": [
            line
            for index, line in enumerate(traceback.format_exception(exc_type, exc_value, exc_traceback))
            if index != 1
        ],
        "details": details,
        "additional_info": additional_info,
    }
    setattr(exception, "response_dict", error_dict)
    setattr(exception, "response_status", response_status)
    return exception