from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.exceptions import TelegramBadRequest
from config import INTERFACE_IMAGES_FOLDER
from utils.message_utils import send_message_with_image
from utils.message_edit_utils import safe_edit_text
from keyboards.main_kb import get_main_keyboard
from services.text_manager import get_text
from utils.emoji import add_emoji_to_text
from config import UNKNOWN_COMMAND, DEFAULT_LANGUAGE
import os

# Создаем роутер для обработчиков главного меню
router = Router()

@router.message()
async def process_main_menu(message: Message, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик текстовых сообщений в главном меню
    """
    text = message.text

    # Получаем тексты кнопок на языке пользователя
    profile_text = add_emoji_to_text("👤", get_text(user_language, "profile_button"))
    learning_text = add_emoji_to_text("📚", get_text(user_language, "learning_center_button"))
    schedule_text = add_emoji_to_text("📆", get_text(user_language, "schedule_button"))
    channel_text = add_emoji_to_text("📢", get_text(user_language, "channel_button"))

    # Проверяем, какая кнопка была нажата
    if text == profile_text:
        # Перенаправляем на обработчик профиля
        from handlers.profile import profile_handler
        return await profile_handler(message, user_language=user_language)

    elif text == learning_text:
        # Перенаправляем на обработчик центра обучения
        from handlers.learning import learning_handler
        return await learning_handler(message, user_language=user_language)

    elif text == schedule_text:
        # Перенаправляем на обработчик расписания
        from handlers.schedule import schedule_handler
        return await schedule_handler(message, user_language=user_language)

    elif text == channel_text:
        # Перенаправляем на обработчик канала
        from handlers.channel import channel_handler
        return await channel_handler(message, user_language=user_language)

    else:
        # Если сообщение не соответствует ни одной кнопке, отправляем сообщение о неизвестной команде
        unknown_command_text = UNKNOWN_COMMAND.get(user_language)
        await message.answer(unknown_command_text)

@router.callback_query(F.data == "back_to_main")
async def back_to_main_callback(callback_query: CallbackQuery, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик возврата в главное меню из других разделов
    """
    # Получаем текст главного меню на языке пользователя
    main_menu_text = get_text(user_language, "main_menu_text")

    # Получаем клавиатуру главного меню
    main_keyboard = get_main_keyboard(user_language)

    # Отвечаем на callback
    await callback_query.answer()

    # Путь к изображению
    image_path = os.path.join(INTERFACE_IMAGES_FOLDER, "main_menu.png")

    # Используем безопасное редактирование текста
    edited = await safe_edit_text(callback_query, main_menu_text, main_keyboard)
    if edited:
        # Отправляем изображение отдельным сообщением
        photo = FSInputFile(image_path)
        await callback_query.message.answer_photo(
            photo=photo,
            caption=main_menu_text,
            reply_markup=main_keyboard
        )
    else:
        # Если не получается отредактировать, отправляем новое сообщение с изображением
        await send_message_with_image(
            message=callback_query.message,
            text=main_menu_text,
            image_path=image_path,
            reply_markup=main_keyboard
        )

def setup_main_menu_handlers(dp):
    """
    Регистрирует обработчики для главного меню
    """
    dp.include_router(router)
