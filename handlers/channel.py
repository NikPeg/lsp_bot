from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.inline_kb import get_channel_keyboard
from services.text_manager import get_text
from utils.emoji import add_emoji_to_text

from config import CHANNEL_LINK

# Создаем роутер для обработчиков канала
router = Router()

@router.message(F.text.startswith("📢"))
async def channel_handler(message: Message):
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

def setup_channel_handlers(dp):
    """
    Регистрирует обработчики для раздела "Наш канал"
    """
    dp.include_router(router)
