REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "utils.exception_handler.drf_exception_response",

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ]
}
