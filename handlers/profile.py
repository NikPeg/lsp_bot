from aiogram import Dispatcher, types
from aiogram.types import InlineKeyboardMarkup

from keyboards.profile_kb import get_faculty_selection_keyboard, get_language_settings_keyboard
from keyboards.language_kb import get_language_keyboard
from keyboards.main_kb import get_main_keyboard

from database.db_manager import set_user_faculty, get_user_faculty, set_user_language

from services.text_manager import get_text
from services.file_manager import get_faculties, check_faculty_exists

from config import PROFILE_INSTRUCTIONS

async def profile_handler(message: types.Message):
    """
    Обработчик нажатия на кнопку "Личный кабинет"
    """
    user_id = message.from_user.id
    user_language = message.data.get('user_language', 'ru')

    # Получаем текущий факультет пользователя
    current_faculty = await get_user_faculty(user_id)

    # Формируем текст профиля
    profile_text = PROFILE_INSTRUCTIONS.get(user_language, PROFILE_INSTRUCTIONS['en'])

    if current_faculty:
        # Проверяем, существует ли факультет в файловой системе
        faculty_exists = await check_faculty_exists(current_faculty)

        if faculty_exists:
            # Получаем ключ для перевода названия факультета
            faculty_key = f"faculty_{current_faculty.split()[0][0]}_name"
            faculty_name = get_text(user_language, faculty_key, default=current_faculty)

            # Добавляем информацию о текущем факультете
            current_faculty_text = get_text(user_language, "current_faculty").format(faculty=faculty_name)
            profile_text += f"\n\n{current_faculty_text}"
        else:
            # Если факультет не существует, уведомляем пользователя
            profile_text += f"\n\n{get_text(user_language, 'faculty_not_found')}"
            # Сбрасываем выбор факультета
            await set_user_faculty(user_id, None)
    else:
        # Если факультет не выбран, добавляем соответствующую информацию
        profile_text += f"\n\n{get_text(user_language, 'no_faculty_selected')}"

    # Получаем клавиатуру с выбором факультета
    keyboard = await get_faculty_selection_keyboard(user_language)

    # Отправляем сообщение с инструкциями и клавиатурой выбора факультета
    await message.answer(
        text=profile_text,
        reply_markup=keyboard
    )

async def faculty_callback(callback_query: types.CallbackQuery, callback_data: dict):
    """
    Обработчик выбора факультета
    """
    user_id = callback_query.from_user.id
    user_language = callback_query.data.get('user_language', 'ru')
    faculty = callback_data["value"]

    # Сохраняем выбранный факультет
    await set_user_faculty(user_id, faculty)

    # Получаем ключ для перевода названия факультета
    faculty_key = f"faculty_{faculty.split()[0][0]}_name"
    faculty_name = get_text(user_language, faculty_key, default=faculty)

    # Формируем текст с информацией о выбранном факультете
    faculty_selected_text = get_text(user_language, "faculty_selected").format(faculty=faculty_name)

    # Отвечаем на callback
    await callback_query.answer(faculty_selected_text)

    # Обновляем текст сообщения
    profile_text = PROFILE_INSTRUCTIONS.get(user_language, PROFILE_INSTRUCTIONS['en'])
    current_faculty_text = get_text(user_language, "current_faculty").format(faculty=faculty_name)
    profile_text += f"\n\n{current_faculty_text}"

    # Получаем обновленную клавиатуру
    keyboard = await get_faculty_selection_keyboard(user_language)

    # Обновляем сообщение
    await callback_query.message.edit_text(
        text=profile_text,
        reply_markup=keyboard
    )

async def open_language_settings_callback(callback_query: types.CallbackQuery):
    """
    Обработчик открытия настроек языка
    """
    user_language = callback_query.data.get('user_language', 'ru')

    # Получаем текст для настроек языка
    language_settings_text = get_text(user_language, "language_settings_text")
    current_language_text = get_text(user_language, "current_language").format(
        language=get_text(user_language, f"language_{user_language}")
    )

    # Формируем полный текст сообщения
    text = f"{language_settings_text}\n\n{current_language_text}"

    # Получаем клавиатуру для выбора языка
    keyboard = get_language_settings_keyboard(user_language)

    # Отвечаем на callback и обновляем сообщение
    await callback_query.answer()
    await callback_query.message.edit_text(
        text=text,
        reply_markup=keyboard
    )

async def change_language_callback(callback_query: types.CallbackQuery, callback_data: dict):
    """
    Обработчик изменения языка из настроек профиля
    """
    user_id = callback_query.from_user.id
    language_code = callback_data["value"]

    # Сохраняем выбранный язык
    await set_user_language(user_id, language_code)

    # Получаем текст для настроек языка на новом языке
    language_settings_text = get_text(language_code, "language_settings_text")
    current_language_text = get_text(language_code, "current_language").format(
        language=get_text(language_code, f"language_{language_code}")
    )

    # Формируем полный текст сообщения
    text = f"{language_settings_text}\n\n{current_language_text}"

    # Получаем клавиатуру для выбора языка
    keyboard = get_language_settings_keyboard(language_code)

    # Отвечаем на callback и обновляем сообщение
    await callback_query.answer(f"Language set to {language_code}")
    await callback_query.message.edit_text(
        text=text,
        reply_markup=keyboard
    )

    # Обновляем клавиатуру главного меню
    main_keyboard = get_main_keyboard(language_code)

    # Отправляем новое сообщение с обновленным главным меню
    main_menu_text = get_text(language_code, "main_menu_text")
    await callback_query.message.answer(
        text=main_menu_text,
        reply_markup=main_keyboard
    )

async def back_to_profile_callback(callback_query: types.CallbackQuery):
    """
    Обработчик возврата к профилю из настроек языка
    """
    user_id = callback_query.from_user.id
    user_language = callback_query.data.get('user_language', 'ru')

    # Получаем текущий факультет пользователя
    current_faculty = await get_user_faculty(user_id)

    # Формируем текст профиля
    profile_text = PROFILE_INSTRUCTIONS.get(user_language, PROFILE_INSTRUCTIONS['en'])

    if current_faculty:
        # Проверяем, существует ли факультет в файловой системе
        faculty_exists = await check_faculty_exists(current_faculty)

        if faculty_exists:
            # Получаем ключ для перевода названия факультета
            faculty_key = f"faculty_{current_faculty.split()[0][0]}_name"
            faculty_name = get_text(user_language, faculty_key, default=current_faculty)

            # Добавляем информацию о текущем факультете
            current_faculty_text = get_text(user_language, "current_faculty").format(faculty=faculty_name)
            profile_text += f"\n\n{current_faculty_text}"
        else:
            # Если факультет не существует, уведомляем пользователя
            profile_text += f"\n\n{get_text(user_language, 'faculty_not_found')}"
            # Сбрасываем выбор факультета
            await set_user_faculty(user_id, None)
    else:
        # Если факультет не выбран, добавляем соответствующую информацию
        profile_text += f"\n\n{get_text(user_language, 'no_faculty_selected')}"

    # Получаем клавиатуру с выбором факультета
    keyboard = await get_faculty_selection_keyboard(user_language)

    # Отвечаем на callback и обновляем сообщение
    await callback_query.answer()
    await callback_query.message.edit_text(
        text=profile_text,
        reply_markup=keyboard
    )

def register_profile_handlers(dp: Dispatcher):
    """
    Регистрирует обработчики для личного кабинета
    """
    dp.register_message_handler(
        profile_handler,
        lambda message: message.text.startswith("👤")
    )

    dp.register_callback_query_handler(
        faculty_callback,
        lambda c: c.data.startswith("faculty:"),
        lambda c: {"value": c.data.split(":")[1]}
    )

    dp.register_callback_query_handler(
        open_language_settings_callback,
        lambda c: c.data == "open_language_settings"
    )

    dp.register_callback_query_handler(
        change_language_callback,
        lambda c: c.data.startswith("change_language:"),
        lambda c: {"value": c.data.split(":")[1]}
    )

    dp.register_callback_query_handler(
        back_to_profile_callback,
        lambda c: c.data == "back_to_profile"
    )
