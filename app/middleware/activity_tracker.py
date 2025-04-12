"""
Middleware для отслеживания активности пользователей.
Обновляет время последней активности при каждом взаимодействии с ботом.
"""

from typing import Callable, Dict, Any, Awaitable
from datetime import datetime

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update, User
from loguru import logger

from app.services.user_service import UserService


class ActivityTrackerMiddleware(BaseMiddleware):
    """
    Middleware для отслеживания активности пользователей.
    Регистрирует время последнего взаимодействия пользователя с ботом.
    """

    def __init__(self):
        """Инициализация middleware."""
        self.user_service = UserService()

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        """
        Обработка входящего события и регистрация активности пользователя.

        Args:
            handler: Обработчик события.
            event: Входящее событие (сообщение, callback и т.д.).
            data: Данные события.

        Returns:
            Any: Результат обработки события.
        """
        # Извлекаем пользователя из события
        user = self._get_user_from_event(event)

        if user:
            # Регистрируем активность пользователя
            try:
                await self.user_service.register_user_activity(user.id)
                logger.debug(f"Активность пользователя {user.id} ({user.full_name}) зарегистрирована")
            except Exception as e:
                logger.error(f"Ошибка при регистрации активности пользователя {user.id}: {e}")

        # Вызываем следующий обработчик
        return await handler(event, data)

    def _get_user_from_event(self, event) -> User or None:
        """
        Извлекает пользователя из разных типов событий.

        Args:
            event: Событие (сообщение, callback и т.д.).

        Returns:
            User: Объект пользователя из события или None, если пользователь не найден.
        """
        if isinstance(event, Message):
            return event.from_user
        elif isinstance(event, CallbackQuery):
            return event.from_user

        # Для других типов событий пробуем получить from_user
        try:
            if hasattr(event, 'from_user'):
                return event.from_user
        except:
            pass

        return None
