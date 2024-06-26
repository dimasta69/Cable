REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "utils.exception_handler.drf_exception_response",
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 15,

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ]
}

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']