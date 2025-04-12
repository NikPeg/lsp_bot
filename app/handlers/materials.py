"""
Модуль обработчиков для работы с учебными материалами (лекции, книги и т.д.).
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger
from pathlib import Path

from app.config import get_config
from app.services.user_activity import UserActivityTracker
from app.services.file_manager import FileManager
from app.utils.helpers import get_text
from app.keyboards.dynamic_kb import (
    get_material_types_keyboard,
    get_semesters_keyboard,
    get_materials_keyboard
)

# Получаем конфигурацию
config = get_config()

# Создаем роутер для работы с материалами
materials_router = Router()

# Инициализация сервисов
user_activity = UserActivityTracker()
file_manager = FileManager()

# Локализованные названия типов материалов
MATERIAL_TYPES = {
    "lectures": {
        "ru": "Лекции",
        "en": "Lectures",
        "ar": "المحاضرات"
    },
    "books": {
        "ru": "Книги",
        "en": "Books",
        "ar": "الكتب"
    },
    "atlases": {
        "ru": "Атласы",
        "en": "Atlases",
        "ar": "الأطالس"
    },
    "methods": {
        "ru": "Методички",
        "en": "Methodological materials",
        "ar": "المواد المنهجية"
    },
    "exams": {
        "ru": "Экзаменационные материалы",
        "en": "Exam materials",
        "ar": "مواد الامتحان"
    },
    "notes": {
        "ru": "Шпаргалки и конспекты",
        "en": "Notes and summaries",
        "ar": "الملاحظات والملخصات"
    }
}

@materials_router.callback_query(F.data.startswith("material_type_"))
async def show_semesters(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора типа материала."""
    user_id = callback.from_user.id
    material_type = callback.data.split('_', 2)[2]

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)
    faculty = user_data.get('faculty')

    state_data = await state.get_data()
    subject = state_data.get("subject")

    if not faculty or not subject:
        await callback.answer(get_text(language, "select_faculty_and_subject_first"))
        return

    await state.update_data(material_type=material_type)

    # Получаем семестры для выбранного типа материала
    semesters = await file_manager.get_semesters(faculty, subject, material_type)

    if not semesters:
        await callback.answer(get_text(language, "no_semesters_found"), show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text(
        f"{get_text(language, 'material_type_selected').format(material_type=MATERIAL_TYPES.get(material_type, {}).get(language, material_type))}\n\n{get_text(language, 'select_semester')}",
        reply_markup=get_semesters_keyboard(material_type, semesters, language)
    )
    logger.info(f"User {user_id} selected material type: {material_type}")

@materials_router.callback_query(F.data.startswith("semester_"))
async def show_materials(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора семестра."""
    user_id = callback.from_user.id
    parts = callback.data.split('_')
    material_type = parts[1]
    semester = parts[2]

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)
    faculty = user_data.get('faculty')

    state_data = await state.get_data()
    subject = state_data.get("subject")

    if not faculty or not subject:
        await callback.answer(get_text(language, "select_faculty_and_subject_first"))
        return

    await state.update_data(semester=semester)

    # Получаем материалы для выбранного семестра
    materials = await file_manager.get_files(faculty, subject, material_type, semester)

    if not materials:
        await callback.answer(get_text(language, "no_materials_found"), show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text(
        f"{get_text(language, 'semester_selected').format(semester=semester)}\n\n{get_text(language, 'select_material')}",
        reply_markup=get_materials_keyboard(material_type, semester, materials, language)
    )
    logger.info(f"User {user_id} selected semester: {semester}")

@materials_router.callback_query(F.data.startswith("file_"))
async def send_material_file(callback: CallbackQuery, state: FSMContext):
    """Обработчик отправки выбранного файла."""
    user_id = callback.from_user.id
    parts = callback.data.split('_')
    material_type = parts[1]
    semester = parts[2]
    file_name = '_'.join(parts[3:])

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)
    faculty = user_data.get('faculty')

    state_data = await state.get_data()
    subject = state_data.get("subject")

    if not faculty or not subject:
        await callback.answer(get_text(language, "select_faculty_and_subject_first"))
        return

    await callback.answer()

    # Получаем путь к файлу
    file_path = await file_manager.get_file_path(faculty, subject, material_type, semester, file_name)

    if not file_path or not file_path.exists():
        await callback.message.answer(get_text(language, "file_not_found"))
        logger.error(f"File not found: {file_path}")
        return

    try:
        # Отправляем информацию о файле
        await callback.message.answer(
            get_text(language, "material_info").format(
                subject=subject,
                type=MATERIAL_TYPES.get(material_type, {}).get(language, material_type),
                semester=semester,
                name=file_path.stem
            )
        )

        # Отправляем сам файл
        with open(file_path, 'rb') as file:
            if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                await callback.message.answer_photo(
                    photo=file,
                    caption=file_path.stem,
                    protect_content=True
                )
            else:
                await callback.message.answer_document(
                    document=file,
                    caption=file_path.stem,
                    protect_content=True
                )

        logger.info(f"User {user_id} received file: {file_path.name}")

    except Exception as e:
        await callback.message.answer(get_text(language, "error_sending_file"))
        logger.error(f"Error sending file {file_path}: {e}")

@materials_router.callback_query(F.data == "back_to_material_types")
async def back_to_material_types(callback: CallbackQuery, state: FSMContext):
    """Обработчик возврата к выбору типа материала."""
    user_id = callback.from_user.id

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)
    faculty = user_data.get('faculty')

    state_data = await state.get_data()
    subject = state_data.get("subject")

    if not faculty or not subject:
        await callback.answer(get_text(language, "select_faculty_and_subject_first"))
        return

    await callback.answer()
    await callback.message.edit_text(
        get_text(language, "select_material_type"),
        reply_markup=get_material_types_keyboard(
            ["lectures", "books", "atlases", "methods", "exams", "notes"],
            language
        )
    )
    logger.info(f"User {user_id} returned to material types selection")

@materials_router.callback_query(F.data == "back_to_semesters")
async def back_to_semesters(callback: CallbackQuery, state: FSMContext):
    """Обработчик возврата к выбору семестра."""
    user_id = callback.from_user.id
    user_activity.update_activity(user_id)

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)
    faculty = user_data.get('faculty')

    state_data = await state.get_data()
    subject = state_data.get("subject")
    material_type = state_data.get("material_type")

    if not all([faculty, subject, material_type]):
        await callback.answer(get_text(language, "missing_data"))
        return

    # Получаем список семестров для выбранного типа материала
    semesters = await file_manager.get_semesters(faculty, subject, material_type)

    if not semesters:
        await callback.answer(get_text(language, "no_semesters_found"), show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_text(
        f"{get_text(language, 'material_type_selected').format(material_type=MATERIAL_TYPES.get(material_type, {}).get(language, material_type))}\n\n{get_text(language, 'select_semester')}",
        reply_markup=get_semesters_keyboard(material_type, semesters, language)
    )
    logger.info(f"User {user_id} returned to semester selection for {material_type}")

# Вспомогательные функции для работы с файлами
async def send_file(message: Message, file_path: Path, language: str):
    """Универсальная функция для отправки файла с обработкой ошибок."""
    try:
        if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            await message.answer_photo(
                photo=InputFile(file_path),
                caption=file_path.stem,
                protect_content=True
            )
        else:
            await message.answer_document(
                document=InputFile(file_path),
                caption=file_path.stem,
                protect_content=True
            )
        return True
    except Exception as e:
        logger.error(f"Error sending file {file_path}: {e}")
        await message.answer(get_text(language, "error_sending_file"))
        return False

def get_material_type_display_name(material_type: str, language: str) -> str:
    """Возвращает локализованное название типа материала."""
    return MATERIAL_TYPES.get(material_type, {}).get(language, material_type)
