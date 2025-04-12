"""
Middleware для автоматического добавления защиты от пересылки ко всем исходящим сообщениям.
"""

from typing import Callable, Dict, Any, Awaitable, Optional, cast

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.dispatcher.flags import get_flag
from aiogram.methods.base import TelegramMethod

class AntiForwardMiddleware(BaseMiddleware):
    """
    Middleware для автоматического добавления защиты от пересылки ко всем исходящим сообщениям.
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        """
        Обработка входящего события и модификация ответов для предотвращения пересылки.

        Args:
            handler: Обработчик события.
            event: Входящее событие (сообщение, callback и т.д.).
            data: Данные события.

        Returns:
            Any: Результат обработки события.
        """
        # Получаем результат выполнения обработчика
        result = await handler(event, data)

        # Если результат - это метод Telegram API или список методов
        if isinstance(result, TelegramMethod):
            # Пытаемся установить protect_content=True, если это возможно
            if hasattr(result, 'protect_content'):
                setattr(result, 'protect_content', True)

        elif isinstance(result, list) and all(isinstance(item, TelegramMethod) for item in result):
            # Обрабатываем список методов
            for item in result:
                if hasattr(item, 'protect_content'):
                    setattr(item, 'protect_content', True)

        return result


# Примечание: этот middleware не будет работать для всех методов отправки сообщений,
# так как aiogram 3.x использует отложенную отправку сообщений.
# В большинстве случаев лучше указывать параметр protect_content=True напрямую
# при вызове методов send_message, answer_photo и т.д.
