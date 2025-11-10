"""
WSGI config for catalog project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os  # noqa: I001
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

from container import container  # noqa: I001
from main.integrations import setup_dishka

# регистрируем контейнер в Django settings
setup_dishka(container)

# создаём WSGI-приложение
application = get_wsgi_application()
