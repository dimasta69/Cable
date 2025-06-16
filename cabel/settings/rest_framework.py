from datetime import timedelta

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    "EXCEPTION_HANDLER": "utils.exception_handler.drf_exception_response",
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    'PAGE_SIZE': 15,
}

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'JWT Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': "JWT Authorization header using the Token scheme. Example: \"Token {token}\""
        }
    },
}
