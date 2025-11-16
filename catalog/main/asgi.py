"""
ASGI config for catalog project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os  # noqa: I001
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

from container import container  # noqa: I001
from main.integrations import setup_dishka

setup_dishka(container)

application = get_asgi_application()
