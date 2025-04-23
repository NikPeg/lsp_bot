from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Command

from keyboards.language_kb import get_language_keyboard
from keyboards.main_kb import get_main_keyboard
from database.db_manager import set_user_language, get_user_language
from config import DEFAULT_LANGUAGE
from services.text_manager import get_text

async def cmd_start(message: types.Message):
    """
    Обработчик команды /start - отправляет приветствие и предлагает выбрать язык
    """
    keyboard = get_language_keyboard()

    # Отправляем сообщение с выбором языка
    await message.answer(
        text="🌐 Please select your language / Пожалуйста, выберите язык / الرجاء اختيار لغتك",
        reply_markup=keyboard
    )

async def language_callback(callback_query: types.CallbackQuery, callback_data: dict):
    """
    Обработчик выбора языка из инлайн-клавиатуры
    """
    # Получаем выбранный язык из callback_data
    language_code = callback_data["value"]
    user_id = callback_query.from_user.id

    # Сохраняем выбранный язык в базу данных
    await set_user_language(user_id, language_code)

    # Получаем приветственный текст на выбранном языке
    welcome_text = get_text(language_code, "welcome_text")

    # Создаем основную клавиатуру на выбранном языке
    main_keyboard = get_main_keyboard(language_code)

    # Отвечаем на callback и обновляем сообщение
    await callback_query.answer(f"Language set to {language_code}")
    await callback_query.message.edit_text(welcome_text)

    # Отправляем новое сообщение с главным меню
    main_menu_text = get_text(language_code, "main_menu_text")
    await callback_query.message.answer(
        text=main_menu_text,
        reply_markup=main_keyboard
    )

def register_start_handlers(dp: Dispatcher):
    """
    Регистрирует обработчики для команды старта и выбора языка
    """
    dp.register_message_handler(cmd_start, Command("start"))
    dp.register_callback_query_handler(
        language_callback,
        lambda c: c.data.startswith("language:"),
        lambda c: {"value": c.data.split(":")[1]}
    )
