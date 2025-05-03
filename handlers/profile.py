from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.profile_kb import get_language_settings_keyboard
from keyboards.language_kb import get_language_keyboard
from keyboards.main_kb import get_main_keyboard
from config import INTERFACE_IMAGES_FOLDER
from utils.message_utils import send_message_with_image
import os
from database.db_manager import set_user_faculty, get_user_faculty, set_user_language

from services.text_manager import get_text
from services.file_manager import get_faculties, check_faculty_exists

from config import PROFILE_INSTRUCTIONS, DEFAULT_LANGUAGE
from utils.emoji import add_emoji_to_text

# Создаем роутер для обработчиков профиля
router = Router()

# Список университетов
UNIVERSITIES = [
    "Санкт-Петербургский государственный педиатрический медицинский университет",
    "Военно-медицинская академия имени С. М. Кирова",
    "Северо-Западный государственный медицинский университет им. И.И.Мечникова",
    "УНИВЕРСИТЕТ РЕАВИЗ",
    "Санкт-Петербургский медико-социальный институт"
]

# Короткие имена для университетов (для callback_data)
UNIVERSITY_SHORTCUTS = {
    "Санкт-Петербургский государственный педиатрический медицинский университет": "spbgpmu",
    "Военно-медицинская академия имени С. М. Кирова": "vmeda",
    "Северо-Западный государственный медицинский университет им. И.И.Мечникова": "szgmu",
    "УНИВЕРСИТЕТ РЕАВИЗ": "reaviz",
    "Санкт-Петербургский медико-социальный институт": "spbmsi"
}

# Обратный словарь для получения полного названия по короткому имени
UNIVERSITY_NAMES = {v: k for k, v in UNIVERSITY_SHORTCUTS.items()}

# Функция для получения клавиатуры выбора университета
async def get_university_selection_keyboard(language: str, selected_university: str = None) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для выбора университета

    Аргументы:
        language (str): Код языка (ru, en, ar)
        selected_university (str, optional): Короткое имя выбранного университета

    Возвращает:
        InlineKeyboardMarkup: Клавиатура с кнопками университетов
    """
    builder = InlineKeyboardBuilder()

    for university in UNIVERSITIES:
        # Получаем короткое имя для callback_data
        univ_shortcut = UNIVERSITY_SHORTCUTS.get(university, "unknown")

        # Создаем текст кнопки, добавляем галочку для выбранного университета
        # Используем только первые 30 символов для отображения, чтобы кнопки не были слишком длинными
        univ_text = university[:30] + "..." if len(university) > 30 else university

        if univ_shortcut == selected_university:
            univ_text = add_emoji_to_text("🏛️", univ_text) + " ✅"
        else:
            univ_text = add_emoji_to_text("🏛️", univ_text)

        builder.row(
            InlineKeyboardButton(text=univ_text, callback_data=f"univ:{univ_shortcut}")
        )

    # Добавляем кнопку для выбора языка
    language_settings_text = add_emoji_to_text("🌐", get_text(language, "language_settings_button"))
    builder.row(
        InlineKeyboardButton(text=language_settings_text, callback_data="open_language_settings")
    )

    # Добавляем кнопку для возврата в главное меню
    back_text = add_emoji_to_text("🔙", get_text(language, "back_to_main_menu"))
    builder.row(
        InlineKeyboardButton(text=back_text, callback_data="back_to_main")
    )

    return builder.as_markup()

# Создаем функцию для получения клавиатуры с выбором факультета
async def get_faculty_selection_keyboard_with_selected(language: str, selected_university: str = None, selected_faculty: str = None) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для выбора факультета с отметкой выбранного

    Аргументы:
        language (str): Код языка (ru, en, ar)
        selected_university (str, optional): Короткое имя выбранного университета
        selected_faculty (str, optional): Выбранный факультет

    Возвращает:
        InlineKeyboardMarkup: Клавиатура с кнопками факультетов
    """
    builder = InlineKeyboardBuilder()

    # Добавляем информацию о выбранном университете
    if selected_university:
        university_name = UNIVERSITY_NAMES.get(selected_university, selected_university)
        university_text = university_name[:30] + "..." if len(university_name) > 30 else university_name
        university_text = add_emoji_to_text("🏛️", university_text) + " ✅"
        builder.row(
            InlineKeyboardButton(text=university_text, callback_data=f"back_to_univ")
        )

    # Получаем список факультетов из файловой системы
    faculties = await get_faculties()

    # Добавляем кнопку для каждого факультета
    for faculty in faculties:
        # Пытаемся найти перевод названия факультета
        faculty_key = f"faculty_{faculty.split()[0][0]}_name"  # Например, "faculty_L_name" для "Лечебный факультет"
        faculty_text = get_text(language, faculty_key, default=faculty)

        # Добавляем галочку, если это выбранный факультет
        if faculty == selected_faculty:
            faculty_text = add_emoji_to_text("🏫", faculty_text) + " ✅"
        else:
            faculty_text = add_emoji_to_text("🏫", faculty_text)

        builder.row(
            InlineKeyboardButton(text=faculty_text, callback_data=f"faculty:{faculty}")
        )

    # Добавляем кнопку для выбора языка
    language_settings_text = add_emoji_to_text("🌐", get_text(language, "language_settings_button"))
    builder.row(
        InlineKeyboardButton(text=language_settings_text, callback_data="open_language_settings")
    )

    # Добавляем кнопку для возврата в главное меню
    back_text = add_emoji_to_text("🔙", get_text(language, "back_to_main_menu"))
    builder.row(
        InlineKeyboardButton(text=back_text, callback_data="back_to_main")
    )

    return builder.as_markup()

@router.message(F.text.startswith("👤"))
async def profile_handler(message: Message, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик нажатия на кнопку "Личный кабинет"
    """
    user_id = message.from_user.id

    # Формируем текст профиля
    profile_text = PROFILE_INSTRUCTIONS.get(user_language, PROFILE_INSTRUCTIONS['en'])
    profile_text += f"\n\n{get_text(user_language, 'select_university')}"

    # Получаем клавиатуру с выбором университета
    # По умолчанию выбираем первый университет в списке
    selected_university = "spbgpmu"  # СПбГПМУ по умолчанию
    keyboard = await get_university_selection_keyboard(user_language, selected_university)

    # Путь к изображению
    image_path = os.path.join(INTERFACE_IMAGES_FOLDER, "profile.png")

    # Отправляем сообщение с изображением
    await send_message_with_image(
        message=message,
        text=profile_text,
        image_path=image_path,
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("univ:"))
async def university_callback(callback_query: CallbackQuery, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик выбора университета
    """
    university_shortcut = callback_query.data.split(":")[1]
    user_id = callback_query.from_user.id

    # Отвечаем на callback
    await callback_query.answer(f"Выбран университет: {UNIVERSITY_NAMES.get(university_shortcut, university_shortcut)[:20]}...")

    # Получаем текущий факультет пользователя
    current_faculty = await get_user_faculty(user_id)

    # Формируем текст сообщения для выбора факультета
    profile_text = PROFILE_INSTRUCTIONS.get(user_language, PROFILE_INSTRUCTIONS['en'])
    profile_text += f"\n\n{get_text(user_language, 'select_faculty')}"

    # Получаем клавиатуру с выбором факультета
    keyboard = await get_faculty_selection_keyboard_with_selected(user_language, university_shortcut, current_faculty)

    # Путь к изображению
    image_path = os.path.join(INTERFACE_IMAGES_FOLDER, "profile.png")

    # Проверяем, есть ли у сообщения фото
    if callback_query.message.photo:
        try:
            # Если это фото, пытаемся обновить подпись и клавиатуру
            await callback_query.message.edit_caption(
                caption=profile_text,
                reply_markup=keyboard
            )
            return
        except Exception as e:
            print(f"Error editing caption: {e}")

    try:
        # Пробуем удалить предыдущее сообщение, если не удалось обновить подпись
        await callback_query.message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")

    # Отправляем новое сообщение с изображением
    await send_message_with_image(
        message=callback_query.message,
        text=profile_text,
        image_path=image_path,
        reply_markup=keyboard
    )

@router.callback_query(F.data == "back_to_univ")
async def back_to_university_callback(callback_query: CallbackQuery, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик возврата к выбору университета
    """
    # Формируем текст профиля
    profile_text = PROFILE_INSTRUCTIONS.get(user_language, PROFILE_INSTRUCTIONS['en'])
    profile_text += f"\n\n{get_text(user_language, 'select_university')}"

    # Получаем клавиатуру с выбором университета
    # По умолчанию выбираем первый университет в списке
    selected_university = "spbgpmu"  # СПбГПМУ по умолчанию
    keyboard = await get_university_selection_keyboard(user_language, selected_university)

    # Путь к изображению
    image_path = os.path.join(INTERFACE_IMAGES_FOLDER, "profile.png")

    # Отвечаем на callback
    await callback_query.answer()

    # Проверяем, есть ли у сообщения фото
    if callback_query.message.photo:
        try:
            # Если это фото, пытаемся обновить подпись и клавиатуру
            await callback_query.message.edit_caption(
                caption=profile_text,
                reply_markup=keyboard
            )
            return
        except Exception as e:
            print(f"Error editing caption: {e}")

    try:
        # Пробуем удалить предыдущее сообщение, если не удалось обновить подпись
        await callback_query.message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")

    # Отправляем новое сообщение с изображением
    await send_message_with_image(
        message=callback_query.message,
        text=profile_text,
        image_path=image_path,
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

    # Формируем текст с информацией о выбранном университете и факультете
    profile_text = PROFILE_INSTRUCTIONS.get(user_language, PROFILE_INSTRUCTIONS['en'])
    profile_text += f"\n\n{get_text(user_language, 'select_faculty')}"

    # По умолчанию выбираем первый университет в списке
    selected_university = "spbgpmu"  # СПбГПМУ по умолчанию

    # Получаем обновленную клавиатуру с отмеченным выбранным факультетом
    keyboard = await get_faculty_selection_keyboard_with_selected(user_language, selected_university, faculty)

    # Путь к изображению
    image_path = os.path.join(INTERFACE_IMAGES_FOLDER, "profile.png")

    # Проверяем, есть ли у сообщения фото
    if callback_query.message.photo:
        try:
            # Если это фото, пытаемся обновить подпись и клавиатуру
            await callback_query.message.edit_caption(
                caption=profile_text,
                reply_markup=keyboard
            )
            return
        except Exception as e:
            print(f"Error editing caption: {e}")

    try:
        # Пробуем удалить предыдущее сообщение, если не удалось обновить подпись
        await callback_query.message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")

    # Отправляем новое сообщение с изображением
    await send_message_with_image(
        message=callback_query.message,
        text=profile_text,
        image_path=image_path,
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

    # Проверяем, есть ли у сообщения фото
    if callback_query.message.photo:
        try:
            # Пробуем удалить предыдущее сообщение
            await callback_query.message.delete()
        except Exception as e:
            print(f"Error deleting message: {e}")

        # Отправляем новое текстовое сообщение
        await callback_query.message.answer(
            text=text,
            reply_markup=keyboard
        )
    else:
        # Отвечаем на callback и обновляем текстовое сообщение
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
    # Формируем текст профиля
    profile_text = PROFILE_INSTRUCTIONS.get(user_language, PROFILE_INSTRUCTIONS['en'])
    profile_text += f"\n\n{get_text(user_language, 'select_university')}"

    # Получаем клавиатуру с выбором университета
    # По умолчанию выбираем первый университет в списке
    selected_university = "spbgpmu"  # СПбГПМУ по умолчанию
    keyboard = await get_university_selection_keyboard(user_language, selected_university)

    # Путь к изображению
    image_path = os.path.join(INTERFACE_IMAGES_FOLDER, "profile.png")

    # Отвечаем на callback
    await callback_query.answer()

    # Удаляем текущее сообщение и отправляем новое с изображением
    try:
        await callback_query.message.delete()
    except Exception as e:
        print(f"Error deleting message: {e}")

    # Отправляем новое сообщение с изображением
    await send_message_with_image(
        message=callback_query.message,
        text=profile_text,
        image_path=image_path,
        reply_markup=keyboard
    )

def setup_profile_handlers(dp):
    """
    Регистрирует обработчики для личного кабинета
    """
    dp.include_router(router)
