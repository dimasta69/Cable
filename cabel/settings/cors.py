CORS_ALLOWED_ORIGINS = [
    "http://212.67.12.63:8000",
    "http://localhost:8000",  
]
CSRF_TRUSTED_ORIGINS = ["http://212.67.12.63",]

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
]

CORS_ALLOW_CREDENTIALS = True 