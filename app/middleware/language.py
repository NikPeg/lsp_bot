"""
Middleware для работы с языками пользователей.
Автоматически определяет язык пользователя и добавляет его в данные обработчика.
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from app.config import get_config
from app.services.user_activity import UserActivityTracker

config = get_config()

class LanguageMiddleware(BaseMiddleware):
    """
    Middleware для работы с языками пользователей.
    Автоматически определяет язык пользователя и обновляет время его активности.
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
        Обработка входящего события.

        Args:
            handler: Обработчик события.
            event: Входящее событие (сообщение, callback и т.д.).
            data: Данные события.

        Returns:
            Any: Результат обработки события.
        """
        # Определяем ID пользователя
        user_id = None

        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id is not None:
            # Получаем данные пользователя
            user_data = self.user_activity.get_user_activity(user_id)

            # Если пользователь новый - регистрируем
            if not user_data:
                self.user_activity.register_user(user_id)
                user_data = self.user_activity.get_user_activity(user_id)

            # Получаем язык пользователя или устанавливаем по умолчанию
            user_language = user_data.get('language', config.LANGUAGE_DEFAULT)

            # Добавляем язык в данные обработчика
            data["user_language"] = user_language

            # Обновляем время последней активности пользователя
            self.user_activity.update_activity(user_id)

        # Вызываем следующий обработчик
        return await handler(event, data)
