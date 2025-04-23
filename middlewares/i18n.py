from aiogram import types, Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler

from database.db_manager import get_user_language
from services.text_manager import get_text
from config import DEFAULT_LANGUAGE

class I18nMiddleware(BaseMiddleware):
    """
    Middleware для обработки локализации сообщений бота
    """

    async def on_pre_process_message(self, message: types.Message, data: dict):
        """
        Добавляет язык пользователя в data перед обработкой сообщения
        """
        user_id = message.from_user.id
        language = await get_user_language(user_id) or DEFAULT_LANGUAGE
        data['user_language'] = language

    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        """
        Добавляет язык пользователя в data перед обработкой callback
        """
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id) or DEFAULT_LANGUAGE
        data['user_language'] = language

def setup_middleware(dp: Dispatcher):
    """
    Устанавливает middleware для диспетчера
    """
    dp.middleware.setup(I18nMiddleware())
