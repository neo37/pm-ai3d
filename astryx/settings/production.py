import os

from .base import *

DEBUG = False

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")

ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS",
    "pm.ai3d.art,www.pm.ai3d.art,astryx.atmeta.com,155.212.166.158,localhost,127.0.0.1",
).split(",")

CSRF_TRUSTED_ORIGINS = [
    "https://pm.ai3d.art",
    "https://www.pm.ai3d.art",
    "https://astryx.atmeta.com",
]

WAGTAILADMIN_BASE_URL = "https://pm.ai3d.art"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# WhiteNoise already ships compressed+hashed static files.
STORAGES["staticfiles"]["BACKEND"] = "whitenoise.storage.CompressedManifestStaticFilesStorage"

try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
