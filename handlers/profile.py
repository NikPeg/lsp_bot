from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.profile_kb import get_faculty_selection_keyboard, get_language_settings_keyboard
from keyboards.language_kb import get_language_keyboard
from keyboards.main_kb import get_main_keyboard

from database.db_manager import set_user_faculty, get_user_faculty, set_user_language

from services.text_manager import get_text
from services.file_manager import get_faculties, check_faculty_exists

from config import PROFILE_INSTRUCTIONS, DEFAULT_LANGUAGE

# Создаем роутер для обработчиков профиля
router = Router()

@router.message(F.text.startswith("👤"))
async def profile_handler(message: Message, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик нажатия на кнопку "Личный кабинет"
    """
    user_id = message.from_user.id

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

@router.callback_query(F.data.startswith("faculty:"))
async def faculty_callback(callback_query: CallbackQuery, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик выбора факультета
    """
    user_id = callback_query.from_user.id
    faculty = callback_query.data.split(":")[1]

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

@router.callback_query(F.data == "open_language_settings")
async def open_language_settings_callback(callback_query: CallbackQuery, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик открытия настроек языка
    """
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

@router.callback_query(F.data.startswith("change_language:"))
async def change_language_callback(callback_query: CallbackQuery, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик изменения языка из настроек профиля
    """
    user_id = callback_query.from_user.id
    language_code = callback_query.data.split(":")[1]

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

@router.callback_query(F.data == "back_to_profile")
async def back_to_profile_callback(callback_query: CallbackQuery, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик возврата к профилю из настроек языка
    """
    user_id = callback_query.from_user.id

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

def setup_profile_handlers(dp):
    """
    Регистрирует обработчики для личного кабинета
    """
    dp.include_router(router)
