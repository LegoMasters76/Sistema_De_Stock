"""Select the Django settings module from DJANGO_ENV."""

import os

environment = os.environ.get("DJANGO_ENV", "local").strip().lower()

if environment == "production":
    from .production import *  # noqa: F401,F403
else:
    from .local import *  # noqa: F401,F403