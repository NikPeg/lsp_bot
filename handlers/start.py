from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from keyboards.language_kb import get_language_keyboard
from keyboards.main_kb import get_main_keyboard
from database.db_manager import set_user_language, get_user_language
from config import DEFAULT_LANGUAGE
from services.text_manager import get_text
from config import INTERFACE_IMAGES_FOLDER, DEFAULT_LANGUAGE
from utils.message_utils import send_message_with_image
import os

# Создаем роутер для обработчиков старта
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обработчик команды /start - отправляет приветствие и предлагает выбрать язык
    """
    keyboard = get_language_keyboard()

    # Отправляем сообщение с выбором языка
    await message.answer(
        text="🌐 Please select your language / Пожалуйста, выберите язык / الرجاء اختيار لغتك",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("language:"))
async def language_callback(callback_query: CallbackQuery):
    """
    Обработчик выбора языка из инлайн-клавиатуры
    """
    # Получаем выбранный язык из callback_data
    language_code = callback_query.data.split(":")[1]
    user_id = callback_query.from_user.id

    # Сохраняем выбранный язык в базу данных
    await set_user_language(user_id, language_code)

    # Получаем приветственный текст на выбранном языке
    welcome_text = get_text(language_code, "welcome_text")

    # Создаем основную клавиатуру на выбранном языке
    main_keyboard = get_main_keyboard(language_code)

    # Путь к изображению
    image_path = os.path.join(INTERFACE_IMAGES_FOLDER, "main_menu.png")

    # Отвечаем на callback
    await callback_query.answer(f"Language set to {language_code}")

    try:
        # Пробуем изменить текущее сообщение, только если оно отличается от текущего
        current_text = callback_query.message.text or callback_query.message.caption or ""
        if current_text != welcome_text:
            await callback_query.message.edit_text(welcome_text)
    except Exception as e:
        # Если возникла ошибка при редактировании, просто логируем ее и продолжаем
        print(f"Error editing message: {e}")

    main_menu_text = get_text(language_code, "main_menu_text")
    # Отправляем новое сообщение с главным меню и изображением
    await send_message_with_image(
        message=callback_query.message,
        text=main_menu_text,
        image_path=image_path,
        reply_markup=main_keyboard
    )

def setup_start_handlers(dp):
    """
    Регистрирует обработчики для команды старта и выбора языка
    """
    dp.include_router(router)
