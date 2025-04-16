"""
Модуль обработчиков для центра обучения.
Содержит функционал для доступа к учебным материалам.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger
from pathlib import Path

from app.config import get_config
from app.handlers.start import UserStates
from app.keyboards.learning_center_kb import get_learning_center_keyboard
from app.keyboards.main_menu_kb import get_main_menu_keyboard
from app.keyboards.language_kb import get_language_keyboard
from app.services.user_activity import UserActivityTracker
from app.services.file_manager import FileManager
from app.utils.helpers import get_text

# Получаем конфигурацию
config = get_config()

# Создаем роутер для центра обучения
learning_center_router = Router()

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

@learning_center_router.callback_query(F.data == "learning_center")
async def show_learning_center(callback: CallbackQuery, state: FSMContext):
    """Обработчик перехода в центр обучения."""
    user_id = callback.from_user.id
    user_activity.update_activity(user_id)

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)

    await callback.answer()
    await callback.message.edit_text(
        get_text(language, "learning_center_text"),
        reply_markup=get_learning_center_keyboard(language)
    )
    logger.info(f"User {user_id} opened learning center")

@learning_center_router.callback_query(F.data == "study_center")
async def show_study_center(callback: CallbackQuery, state: FSMContext):
    """Обработчик перехода в учебный центр."""
    user_id = callback.from_user.id
    user_activity.update_activity(user_id)

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)
    faculty = user_data.get('faculty')

    if not faculty:
        await callback.answer()
        await callback.message.edit_text(
            get_text(language, "please_select_faculty"),
            reply_markup=get_faculty_keyboard(language)
        )
        logger.info(f"User {user_id} tried to access study center without faculty")
        return

    subjects = await file_manager.get_subjects(faculty)

    logger.debug(f"Requested subjects for faculty: {faculty}")
    logger.debug(f"Found subjects: {[s.id for s in subjects] if subjects else 'None'}")
    logger.debug(f"Faculty path: {file_manager.base_path / f'faculty_{faculty}'}")

    if not subjects:
        logger.error(f"No subjects found for faculty {faculty}. Checking directory structure...")

        # Проверка существования папки факультета
        faculty_path = file_manager.base_path / f"faculty_{faculty}"
        if not faculty_path.exists():
            logger.error(f"Faculty directory does not exist: {faculty_path}")
        else:
            import os
            logger.debug(f"Faculty directory content: {os.listdir(faculty_path)}")

        await callback.answer(get_text(language, "no_subjects_found"))
        await callback.message.edit_text(
            get_text(language, "no_subjects_found"),
            reply_markup=get_learning_center_keyboard(language)
        )
        return

    await callback.answer()
    await callback.message.edit_text(
        get_text(language, "select_subject"),
        reply_markup=get_subject_keyboard(subjects, language)
    )
    logger.info(f"User {user_id} viewing subjects for faculty {faculty}")

@learning_center_router.callback_query(F.data.startswith("subject_"))
async def process_subject_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора предмета."""
    user_id = callback.from_user.id
    subject_id = callback.data.split('_', 1)[1]

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)
    faculty = user_data.get('faculty')

    await state.update_data(selected_subject=subject_id)

    material_types = ["lectures", "books", "atlases", "methods", "exams", "notes"]

    await callback.answer()
    await callback.message.edit_text(
        get_text(language, "select_material_type"),
        reply_markup=get_material_type_keyboard(material_types, language)
    )
    logger.info(f"User {user_id} selected subject: {subject_id}")

@learning_center_router.callback_query(F.data.startswith("material_type_"))
async def process_material_type_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора типа материала."""
    user_id = callback.from_user.id
    material_type = callback.data.split('_', 2)[2]

    state_data = await state.get_data()
    subject_id = state_data.get("selected_subject")

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)
    faculty = user_data.get('faculty')

    await state.update_data(selected_material_type=material_type)

    # Получаем доступные семестры для этого типа материалов
    semesters = await file_manager.get_semesters(faculty, subject_id, material_type)

    if not semesters:
        await callback.answer(get_text(language, "no_semesters_found"))
        await callback.message.edit_text(
            get_text(language, "no_semesters_found"),
            reply_markup=get_learning_center_keyboard(language)
        )
        return

    await callback.answer()
    await callback.message.edit_text(
        get_text(language, "select_semester"),
        reply_markup=get_semester_keyboard(semesters, language)
    )
    logger.info(f"User {user_id} selected material type: {material_type}")

@learning_center_router.callback_query(F.data.startswith("semester_"))
async def process_semester_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора семестра."""
    user_id = callback.from_user.id
    semester = callback.data.split('_', 1)[1]

    state_data = await state.get_data()
    subject_id = state_data.get("selected_subject")
    material_type = state_data.get("selected_material_type")

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)
    faculty = user_data.get('faculty')

    await state.update_data(selected_semester=semester)

    # Получаем файлы материалов
    files = await file_manager.get_files(faculty, subject_id, material_type, semester)

    if not files:
        await callback.answer(get_text(language, "no_materials_found_in_semester"))
        await callback.message.edit_text(
            get_text(language, "no_materials_found_in_semester"),
            reply_markup=get_learning_center_keyboard(language)
        )
        return

    await callback.answer()
    await callback.message.edit_text(
        get_text(language, "select_material"),
        reply_markup=get_materials_keyboard(files, language)
    )
    logger.info(f"User {user_id} selected semester: {semester}")

@learning_center_router.callback_query(F.data.startswith("material_"))
async def send_material(callback: CallbackQuery, state: FSMContext):
    """Обработчик отправки выбранного материала."""
    user_id = callback.from_user.id
    file_id = callback.data.split('_', 1)[1]

    state_data = await state.get_data()
    subject_id = state_data.get("selected_subject")
    material_type = state_data.get("selected_material_type")
    semester = state_data.get("selected_semester")

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)
    faculty = user_data.get('faculty')

    await callback.answer()

    # Получаем путь к файлу
    file_path = await file_manager.get_file_path(faculty, subject_id, material_type, semester, file_id)

    if not file_path or not file_path.exists():
        await callback.message.answer(get_text(language, "file_not_found"))
        logger.error(f"File not found: {file_path}")
        return

    try:
        # Формируем информацию о материале
        material_info = get_text(language, "material_info").format(
            subject=subject_id,
            type=MATERIAL_TYPES.get(material_type, {}).get(language, material_type),
            semester=semester,
            name=file_path.stem
        )

        await callback.message.answer(material_info)

        # Определяем тип файла для правильной отправки
        file_extension = file_path.suffix.lower()

        with open(file_path, 'rb') as file:
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
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

        logger.info(f"User {user_id} received material: {file_path.name}")

        # Возвращаем пользователя к списку материалов
        files = await file_manager.get_files(faculty, subject_id, material_type, semester)
        await callback.message.answer(
            get_text(language, "select_material"),
            reply_markup=get_materials_keyboard(files, language)
        )

    except Exception as e:
        logger.error(f"Error sending file {file_path}: {e}")
        await callback.message.answer(get_text(language, "error_sending_file"))

@learning_center_router.callback_query(F.data == "language_settings")
async def show_language_settings(callback: CallbackQuery, state: FSMContext):
    """Обработчик перехода к настройкам языка."""
    user_id = callback.from_user.id
    user_activity.update_activity(user_id)

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)

    await state.set_state(UserStates.language_selection)
    await callback.answer()
    await callback.message.edit_text(
        get_text(language, "language_settings_text"),
        reply_markup=get_language_keyboard()
    )
    logger.info(f"User {user_id} opened language settings")

@learning_center_router.callback_query(F.data == "back_to_menu")
async def hide_learning_center(callback: CallbackQuery, state: FSMContext):
    """Обработчик возврата в главное меню."""
    user_id = callback.from_user.id
    user_activity.update_activity(user_id)

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)

    await state.set_state(UserStates.main_menu)
    await callback.answer()
    await callback.message.edit_text(
        get_text(language, "main_menu_text"),
        reply_markup=get_main_menu_keyboard(language)
    )
    logger.info(f"User {user_id} returned to main menu")

# Вспомогательные функции для генерации клавиатур
def get_faculty_keyboard(language: str):
    """Генерация клавиатуры выбора факультета."""
    from app.keyboards.faculty_kb import get_faculty_keyboard
    return get_faculty_keyboard(language)

def get_subject_keyboard(subjects: list, language: str):
    """Генерация клавиатуры выбора предмета."""
    from app.keyboards.dynamic_kb import get_subjects_keyboard
    return get_subjects_keyboard(subjects, language)

def get_material_type_keyboard(material_types: list, language: str):
    """Генерация клавиатуры выбора типа материала."""
    from app.keyboards.dynamic_kb import get_material_types_keyboard
    return get_material_types_keyboard(material_types, language)

def get_semester_keyboard(semesters: list, language: str):
    """Генерация клавиатуры выбора семестра."""
    from app.keyboards.dynamic_kb import get_semesters_keyboard
    return get_semesters_keyboard(semesters, language)

def get_materials_keyboard(materials: list, language: str):
    """Генерация клавиатуры выбора материала."""
    from app.keyboards.dynamic_kb import get_materials_keyboard
    return get_materials_keyboard(materials, language)
