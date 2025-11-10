from pathlib import Path
from typing import Any

from config import Config
from container import container

BASE_DIR = Path(__file__).resolve().parent.parent

config: Config = container.get(Config)

SECRET_KEY = config.secret.config_secret_key
DEBUG = True
DEBUG_PROPAGATE_EXCEPTIONS = True
ALLOWED_HOSTS = config.secret.allowed_hosts

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'main',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'main.integrations.DishkaMiddleware',
]

ROOT_URLCONF = 'main.urls'
WSGI_APPLICATION = 'main.wsgi.application'

DATABASES: dict[str, dict[str, Any]] = {}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ⚡️ теперь берём из конфига
STATIC_URL = config.static.static_url
STATIC_ROOT = config.static.static_root
MEDIA_URL = config.static.media_url
MEDIA_ROOT = config.static.media_root
