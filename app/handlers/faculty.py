"""
Модуль обработчиков для выбора и настройки факультета.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger

from app.config import get_config
from app.handlers.start import UserStates
from app.keyboards.faculty_kb import get_faculty_keyboard
from app.keyboards.main_menu_kb import get_main_menu_keyboard
from app.keyboards.learning_center_kb import get_learning_center_keyboard
from app.services.user_activity import UserActivityTracker
from app.services.file_manager import FileManager
from app.utils.helpers import get_text

# Получаем конфигурацию
config = get_config()

# Создаем роутер для настройки факультета
faculty_router = Router()

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

@faculty_router.callback_query(F.data == "faculty_settings")
async def show_faculty_settings(callback: CallbackQuery, state: FSMContext):
    """Обработчик перехода к настройкам факультета."""
    user_id = callback.from_user.id
    user_activity.update_activity(user_id)

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)
    current_faculty = user_data.get('faculty')

    # Формируем текст сообщения
    if current_faculty:
        text = get_text(language, "current_faculty").format(
            faculty=get_faculty_name(current_faculty, language)
        )
    else:
        text = get_text(language, "no_faculty_selected")

    await callback.answer()
    await callback.message.edit_text(
        text,
        reply_markup=get_faculty_keyboard(language)
    )
    logger.info(f"User {user_id} opened faculty settings")

@faculty_router.callback_query(F.data.startswith("faculty_"))
async def process_faculty_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора факультета."""
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

    await callback.answer()
    await callback.message.edit_text(
        get_text(language, "faculty_selected").format(
            faculty=get_faculty_name(selected_faculty, language)
        ),
        reply_markup=get_learning_center_keyboard(language)
    )
    logger.info(f"User {user_id} selected faculty: {selected_faculty}")

@faculty_router.message(Command("faculty"))
async def cmd_faculty(message: Message, state: FSMContext):
    """Обработчик команды /faculty."""
    user_id = message.from_user.id
    user_activity.update_activity(user_id)

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)
    current_faculty = user_data.get('faculty')

    # Формируем текст сообщения
    if current_faculty:
        text = get_text(language, "current_faculty").format(
            faculty=get_faculty_name(current_faculty, language)
        )
    else:
        text = get_text(language, "no_faculty_selected")

    await message.answer(
        text,
        reply_markup=get_faculty_keyboard(language)
    )
    logger.info(f"User {user_id} requested faculty info")

def get_faculty_name(faculty_code: str, language: str) -> str:
    """
    Возвращает локализованное название факультета.

    Args:
        faculty_code: Код факультета (L, S, P)
        language: Код языка (ru, en, ar)

    Returns:
        Название факультета на указанном языке
    """
    return FACULTY_NAMES.get(faculty_code, {}).get(language, faculty_code)
