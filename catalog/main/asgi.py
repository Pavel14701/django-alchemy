"""
ASGI config for catalog project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os  # noqa: I001
from django.core.asgi import get_asgi_application

# ⚡️ сначала указываем модуль настроек
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

# теперь можно импортировать контейнер и интеграцию
from container import container  # noqa: I001
from main.integrations import setup_dishka

# регистрируем контейнер в Django settings
setup_dishka(container)

# создаём ASGI-приложение
application = get_asgi_application()
