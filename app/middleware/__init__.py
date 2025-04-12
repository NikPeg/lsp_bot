"""
Инициализация модуля middleware.
Экспортирует все middleware и предоставляет функцию для их настройки.
"""

from aiogram import Dispatcher

from app.middleware.language import LanguageMiddleware
from app.middleware.anti_forward import AntiForwardMiddleware
from app.middleware.activity_tracker import ActivityTrackerMiddleware

# Экспорт всех middleware
__all__ = [
    "LanguageMiddleware",
    "AntiForwardMiddleware",
    "ActivityTrackerMiddleware",
    "setup_middleware"
]


def setup_middleware(dp: Dispatcher):
    """
    Настраивает и подключает все middleware к диспетчеру.

    Args:
        dp (Dispatcher): Экземпляр диспетчера.
    """
    # Регистрируем middleware в нужном порядке:
    # ActivityTrackerMiddleware должен идти первым для регистрации активности
    dp.update.middleware(ActivityTrackerMiddleware())

    # LanguageMiddleware для определения языка пользователя
    dp.update.middleware(LanguageMiddleware())

    # AntiForwardMiddleware для защиты контента (обрабатывает ответы)
    dp.update.middleware(AntiForwardMiddleware())
