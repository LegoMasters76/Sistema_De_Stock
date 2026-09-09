"""Production settings with fail-fast security defaults."""

import os

from .base import *  # noqa: F401,F403

DEBUG = False

if SECRET_KEY == "dev-only-change-me" or len(SECRET_KEY) < 50:
    raise RuntimeError("DJANGO_SECRET_KEY must be a random value of at least 50 characters")

if not ALLOWED_HOSTS:
    raise RuntimeError("DJANGO_ALLOWED_HOSTS must contain at least one host")

if not os.environ.get("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is required in production")

MIDDLEWARE = [
    *MIDDLEWARE,
    "main.middleware.ContentSecurityPolicyMiddleware",
]

SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = "DENY"

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"