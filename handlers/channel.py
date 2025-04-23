from aiogram import Dispatcher, types
from aiogram.types import InlineKeyboardMarkup

from keyboards.inline_kb import get_channel_keyboard
from services.text_manager import get_text
from utils.emoji import add_emoji_to_text

from config import CHANNEL_LINK

async def channel_handler(message: types.Message):
    """
    Обработчик нажатия на кнопку "Наш канал"
    """
    user_language = message.data.get('user_language', 'ru')

    # Формируем текст с приглашением подписаться на канал
    channel_text = get_text(user_language, "channel_text").format(channel_link=CHANNEL_LINK)

    # Получаем клавиатуру с кнопкой для перехода в канал
    keyboard = get_channel_keyboard(user_language)

    # Отправляем сообщение с приглашением
    await message.answer(
        text=channel_text,
        reply_markup=keyboard,
        disable_web_page_preview=False  # Разрешаем предпросмотр ссылки
    )

def register_channel_handlers(dp: Dispatcher):
    """
    Регистрирует обработчики для раздела "Наш канал"
    """
    dp.register_message_handler(
        channel_handler,
        lambda message: message.text.startswith("📢")
    )
