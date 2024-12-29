CORS_ALLOWED_ORIGINS = [
    "http://212.67.12.63:8000",
    "http://localhost",
    "http://127.0.0.1:8000",
    "http://94.131.107.85",
    "http://front:3000",
]
CSRF_TRUSTED_ORIGINS = ["http://212.67.12.63","http://localhost","http://127.0.0.1:8000", "http://front:3000",
                        "http://94.131.107.85"]

CORS_ALLOW_HEADERS = [
    "content-type",
    "authorization",
]

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "OPTIONS",
    "PATH",
]

CORS_ALLOW_CREDENTIALS = True 