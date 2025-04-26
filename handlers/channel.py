from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.inline_kb import get_channel_keyboard
from services.text_manager import get_text
from utils.emoji import add_emoji_to_text
from config import INTERFACE_IMAGES_FOLDER, CHANNEL_LINK
from utils.message_utils import send_message_with_image
import os
from config import CHANNEL_LINK, DEFAULT_LANGUAGE

# Создаем роутер для обработчиков канала
router = Router()

@router.message(F.text.startswith("📢"))
async def channel_handler(message: Message, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик нажатия на кнопку "Наш канал"
    """
    # Формируем текст с приглашением подписаться на канал
    channel_text = get_text(user_language, "channel_text").format(channel_link=CHANNEL_LINK)

    # Получаем клавиатуру с кнопкой для перехода в канал
    keyboard = get_channel_keyboard(user_language)

    # Путь к изображению
    image_path = os.path.join(INTERFACE_IMAGES_FOLDER, "channel.jpg")

    # Отправляем сообщение с изображением
    await send_message_with_image(
        message=message,
        text=channel_text,
        image_path=image_path,
        reply_markup=keyboard
    )

def setup_channel_handlers(dp):
    """
    Регистрирует обработчики для раздела "Наш канал"
    """
    dp.include_router(router)
