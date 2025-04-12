"""
Middleware для отслеживания активности пользователей.
Обновляет время последней активности при каждом взаимодействии с ботом.
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update, User
from loguru import logger

from app.services.user_activity import UserActivityTracker


class ActivityTrackerMiddleware(BaseMiddleware):
    """
    Middleware для отслеживания активности пользователей.
    Регистрирует время последнего взаимодействия пользователя с ботом.
    """

    def __init__(self):
        """Инициализация middleware."""
        self.user_activity = UserActivityTracker()

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        """
        Обработка входящего события и регистрация активности пользователя.
        """
        user = self._get_user_from_event(event)

        if user:
            try:
                # Регистрируем пользователя (если еще не зарегистрирован)
                if not self.user_activity.get_user_activity(user.id):
                    self.user_activity.register_user(user.id)

                # Обновляем время активности
                self.user_activity.update_activity(user.id)
                logger.debug(f"Activity updated for user {user.id} ({user.full_name})")
            except Exception as e:
                logger.error(f"Error updating activity for user {user.id}: {e}")

        return await handler(event, data)

    def _get_user_from_event(self, event) -> User or None:
        """
        Извлекает пользователя из разных типов событий.
        """
        if isinstance(event, (Message, CallbackQuery)):
            return event.from_user

        try:
            if hasattr(event, 'from_user'):
                return event.from_user
        except Exception:
            pass

        return None
