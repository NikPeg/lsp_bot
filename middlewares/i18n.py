from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from database.db_manager import get_user_language
from services.text_manager import get_text
from config import DEFAULT_LANGUAGE

class I18nMiddleware(BaseMiddleware):
    """
    Middleware для обработки локализации сообщений бота
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        """
        Обработчик для всех типов событий
        """
        # Получаем user_id в зависимости от типа события
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        else:
            # Если не удалось определить user_id, пропускаем обработку
            return await handler(event, data)

        # Получаем язык пользователя или используем значение по умолчанию
        language = await get_user_language(user_id) or DEFAULT_LANGUAGE

        # Добавляем язык пользователя в data
        data['user_language'] = language

        # Продолжаем обработку события
        return await handler(event, data)

def setup_middleware(dp):
    """
    Устанавливает middleware для диспетчера
    """
    # Устанавливаем middleware для всех типов сообщений
    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())
