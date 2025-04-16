"""
Модуль обработчиков для личного кабинета (выбор факультета).
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger

from app.config import get_config
from app.keyboards.faculty_kb import get_faculty_keyboard
from app.keyboards.main_menu_kb import get_main_menu_keyboard
from app.services.file_manager import FileManager
from app.services.user_activity import UserActivityTracker
from app.utils.helpers import get_text

# Получаем конфигурацию
config = get_config()

# Создаем роутер для личного кабинета
profile_router = Router()

# Инициализация сервисов
user_activity = UserActivityTracker()
file_manager = FileManager()

# Названия факультетов на разных языках
FACULTY_NAMES = {
    "L": {
        "ru": "Лечебный факультет",
        "en": "Faculty of Medicine",
        "ar": "كلية الطب"
    },
    "S": {
        "ru": "Стоматологический факультет",
        "en": "Faculty of Dentistry",
        "ar": "كلية طب الأسنان"
    },
    "P": {
        "ru": "Педиатрический факультет",
        "en": "Faculty of Pediatrics",
        "ar": "كلية طب الأطفال"
    }
}

@profile_router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик перехода в личный кабинет.
    """
    user_id = callback.from_user.id

    # Обновляем активность пользователя
    user_activity.update_activity(user_id)

    # Получаем данные пользователя
    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)
    current_faculty = user_data.get('faculty')

    # Формируем текст в зависимости от выбранного факультета
    if current_faculty:
        faculty_name = get_faculty_name(current_faculty, language)
        profile_text = get_text(language, "profile_with_faculty").format(faculty=faculty_name)
    else:
        profile_text = get_text(language, "profile_no_faculty")

    # Отвечаем на callback
    await callback.answer()

    # Редактируем сообщение с клавиатурой факультетов
    await callback.message.edit_text(
        profile_text,
        reply_markup=get_faculty_keyboard(language)
    )

    logger.info(f"Пользователь {user_id} открыл личный кабинет")

@profile_router.callback_query(F.data.startswith("faculty_"))
async def process_faculty_selection(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора факультета.
    """
    user_id = callback.from_user.id
    selected_faculty = callback.data.split('_')[1]
    logger.debug(f"Selected faculty: {selected_faculty}")

    # Проверяем существование факультета
    faculties = await file_manager.get_faculties()
    if not any(f.id == selected_faculty for f in faculties):
        await callback.answer(get_text(config.LANGUAGE_DEFAULT, "faculty_not_found"))
        return

    # Обновляем данные пользователя
    user_data = user_activity.get_user_activity(user_id)
    user_data['faculty'] = selected_faculty
    user_activity.update_activity(user_id)
    user_activity._save_data()

    # Получаем язык пользователя
    language = user_data.get('language', config.LANGUAGE_DEFAULT)
    faculty_name = get_faculty_name(selected_faculty, language)

    # Формируем ответ
    await callback.answer()
    await callback.message.edit_text(
        get_text(language, "faculty_selected").format(faculty=faculty_name),
        reply_markup=get_main_menu_keyboard(language)
    )

    logger.info(f"Пользователь {user_id} выбрал факультет: {selected_faculty}")

@profile_router.message(Command("profile"))
async def cmd_profile(message: Message, state: FSMContext):
    """
    Обработчик команды /profile.
    """
    user_id = message.from_user.id

    # Обновляем активность пользователя
    user_activity.update_activity(user_id)

    # Получаем данные пользователя
    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)
    current_faculty = user_data.get('faculty')

    # Формируем текст
    if current_faculty:
        faculty_name = get_faculty_name(current_faculty, language)
        profile_text = get_text(language, "profile_with_faculty").format(faculty=faculty_name)
    else:
        profile_text = get_text(language, "profile_no_faculty")

    # Отправляем сообщение
    await message.answer(
        profile_text,
        reply_markup=get_faculty_keyboard(language)
    )

    logger.info(f"Пользователь {user_id} открыл личный кабинет через команду")

def get_faculty_name(faculty_code: str, language: str) -> str:
    """
    Возвращает локализованное название факультета.
    """
    return FACULTY_NAMES.get(faculty_code, {}).get(language, faculty_code)
