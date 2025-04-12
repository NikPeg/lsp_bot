"""
Модуль обработчиков для работы с учебными материалами (лекции, книги и т.д.).
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputFile
from loguru import logger
from pathlib import Path

from app.config import settings
from app.services.file_system import FileSystemService
from app.services.user_service import UserService
from app.utils.helpers import get_text

# Создаем роутер для работы с материалами
materials_router = Router()

# Сервисы для работы с пользователями и файловой системой
user_service = UserService()
file_system_service = FileSystemService()


@materials_router.callback_query(F.data.startswith("material_type_"))
async def show_semesters(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора типа материала.
    Показывает список доступных семестров для выбранного типа материала.

    Args:
        callback (CallbackQuery): Callback-запрос с выбранным типом материала.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Извлекаем тип материала из данных callback
    material_type = callback.data.split('_', 2)[2]

    # Сохраняем выбранный тип материала в состоянии
    await state.update_data(material_type=material_type)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем выбранный факультет и предмет из состояния
    state_data = await state.get_data()
    faculty = await user_service.get_user_faculty(user_id)
    subject = state_data.get("subject")

    if not faculty or not subject:
        # Если не выбран факультет или предмет, возвращаем в меню
        await callback.answer(get_text(language, "select_faculty_and_subject_first"))
        return

    # Получаем список семестров для выбранного типа материала
    semesters = await file_system_service.get_semesters(faculty, subject, material_type)

    if not semesters:
        # Если семестры не найдены
        no_semesters_text = get_text(language, "no_semesters_found")
        await callback.answer(no_semesters_text, show_alert=True)
        return

    # Получаем текст на нужном языке
    semester_selection_text = get_text(language, "select_semester")

    # Получаем название материала на выбранном языке
    material_type_name = get_material_type_name(material_type, language)

    # Формируем текст с информацией о выбранном типе материала
    info_text = get_text(language, "material_type_selected").format(
        material_type=material_type_name
    )

    # Создаем клавиатуру с семестрами
    keyboard = get_semester_keyboard(material_type, semesters, language)

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение, предлагая выбрать семестр
    await callback.message.edit_text(
        f"{info_text}\n\n{semester_selection_text}",
        reply_markup=keyboard
    )

    logger.info(f"Пользователь {user_id} выбрал тип материала: {material_type}")


@materials_router.callback_query(F.data.startswith("semester_"))
async def show_materials(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора семестра.
    Показывает список доступных материалов для выбранного семестра.

    Args:
        callback (CallbackQuery): Callback-запрос с выбранным семестром.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Извлекаем семестр и тип материала из данных callback
    callback_parts = callback.data.split('_')
    material_type = callback_parts[1]
    semester = callback_parts[2]

    # Сохраняем выбранный семестр в состоянии
    await state.update_data(semester=semester)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем выбранный факультет и предмет из состояния
    state_data = await state.get_data()
    faculty = await user_service.get_user_faculty(user_id)
    subject = state_data.get("subject")

    if not faculty or not subject:
        # Если не выбран факультет или предмет, возвращаем в меню
        await callback.answer(get_text(language, "select_faculty_and_subject_first"))
        return

    # Получаем список материалов для выбранного семестра
    materials = await file_system_service.get_materials(faculty, subject, material_type, semester)

    if not materials:
        # Если материалы не найдены
        no_materials_text = get_text(language, "no_materials_found")
        await callback.answer(no_materials_text, show_alert=True)
        return

    # Получаем текст на нужном языке
    materials_selection_text = get_text(language, "select_material")

    # Формируем текст с информацией о выбранном семестре
    info_text = get_text(language, "semester_selected").format(
        semester=semester
    )

    # Создаем клавиатуру с материалами
    keyboard = get_materials_keyboard(material_type, semester, materials, language)

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение, предлагая выбрать материал
    await callback.message.edit_text(
        f"{info_text}\n\n{materials_selection_text}",
        reply_markup=keyboard
    )

    logger.info(f"Пользователь {user_id} выбрал семестр: {semester}")


@materials_router.callback_query(F.data.startswith("file_"))
async def send_material_file(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора конкретного материала.
    Отправляет выбранный файл пользователю.

    Args:
        callback (CallbackQuery): Callback-запрос с выбранным файлом.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Извлекаем тип материала, семестр и имя файла из данных callback
    callback_parts = callback.data.split('_')
    material_type = callback_parts[1]
    semester = callback_parts[2]
    file_name = '_'.join(callback_parts[3:])  # Обрабатываем случай, если в имени файла есть подчеркивание

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем выбранный факультет и предмет из состояния
    state_data = await state.get_data()
    faculty = await user_service.get_user_faculty(user_id)
    subject = state_data.get("subject")

    if not faculty or not subject:
        # Если не выбран факультет или предмет, возвращаем в меню
        await callback.answer(get_text(language, "select_faculty_and_subject_first"))
        return

    # Получаем путь к файлу
    try:
        file_path = await file_system_service.get_material_path(
            faculty, subject, material_type, semester, file_name
        )

        if not file_path.exists():
            await callback.answer(get_text(language, "file_not_found"), show_alert=True)
            logger.error(f"Файл не найден: {file_path}")
            return

        # Отвечаем на callback, чтобы убрать индикатор загрузки
        await callback.answer()

        # Отправляем сообщение о загрузке файла
        loading_message = await callback.message.answer(get_text(language, "loading_file"))

        # Определяем тип файла и отправляем соответствующим способом
        file_extension = file_path.suffix.lower()

        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            # Отправляем как фото
            await callback.message.answer_photo(
                photo=open(file_path, 'rb'),
                caption=file_name,
                protect_content=True  # Запрет на пересылку
            )
        elif file_extension in ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.ppt', '.pptx']:
            # Отправляем как документ
            await callback.message.answer_document(
                document=open(file_path, 'rb'),
                caption=file_name,
                protect_content=True  # Запрет на пересылку
            )
        else:
            # Отправляем как файл для других типов
            await callback.message.answer_document(
                document=open(file_path, 'rb'),
                caption=file_name,
                protect_content=True  # Запрет на пересылку
            )

        # Удаляем сообщение о загрузке
        await loading_message.delete()

        logger.info(f"Пользователь {user_id} получил файл: {file_name}")

    except Exception as e:
        await callback.message.answer(get_text(language, "error_sending_file"))
        logger.error(f"Ошибка при отправке файла: {e}")


@materials_router.callback_query(F.data == "back_to_material_types")
async def back_to_material_types(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Назад к типам материалов".

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем выбранный факультет и предмет из состояния
    state_data = await state.get_data()
    faculty = await user_service.get_user_faculty(user_id)
    subject = state_data.get("subject")

    if not faculty or not subject:
        # Если не выбран факультет или предмет, возвращаем в меню
        await callback.answer(get_text(language, "select_faculty_and_subject_first"))
        return

    # Получаем доступные типы материалов
    material_types = await file_system_service.get_material_types(faculty, subject)

    if not material_types:
        # Если типы материалов не найдены
        no_materials_text = get_text(language, "no_materials_found")
        await callback.answer(no_materials_text, show_alert=True)
        return

    # Получаем текст на нужном языке
    material_types_text = get_text(language, "select_material_type")

    # Создаем клавиатуру с типами материалов
    keyboard = get_material_types_keyboard(material_types, language)

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение, предлагая выбрать тип материала
    await callback.message.edit_text(
        material_types_text,
        reply_markup=keyboard
    )

    logger.info(f"Пользователь {user_id} вернулся к выбору типа материала")


@materials_router.callback_query(F.data == "back_to_semesters")
async def back_to_semesters(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Назад к семестрам".

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем данные из состояния
    state_data = await state.get_data()
    faculty = await user_service.get_user_faculty(user_id)
    subject = state_data.get("subject")
    material_type = state_data.get("material_type")

    if not faculty or not subject or not material_type:
        # Если не хватает данных, возвращаем в меню
        await callback.answer(get_text(language, "missing_data"))
        return

    # Получаем список семестров для выбранного типа материала
    semesters = await file_system_service.get_semesters(faculty, subject, material_type)

    if not semesters:
        # Если семестры не найдены
        no_semesters_text = get_text(language, "no_semesters_found")
        await callback.answer(no_semesters_text, show_alert=True)
        return

    # Получаем текст на нужном языке
    semester_selection_text = get_text(language, "select_semester")

    # Получаем название материала на выбранном языке
    material_type_name = get_material_type_name(material_type, language)

    # Формируем текст с информацией о выбранном типе материала
    info_text = get_text(language, "material_type_selected").format(
        material_type=material_type_name
    )

    # Создаем клавиатуру с семестрами
    keyboard = get_semester_keyboard(material_type, semesters, language)

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение, предлагая выбрать семестр
    await callback.message.edit_text(
        f"{info_text}\n\n{semester_selection_text}",
        reply_markup=keyboard
    )

    logger.info(f"Пользователь {user_id} вернулся к выбору семестра")


def get_material_type_name(material_type, language):
    """
    Получает название типа материала на нужном языке.

    Args:
        material_type (str): Тип материала.
        language (str): Код языка.

    Returns:
        str: Название типа материала на указанном языке.
    """
    material_types = {
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

    return material_types.get(material_type, {}).get(language, material_type)


# Вспомогательные функции для генерации клавиатур
# В реальном проекте их лучше перенести в отдельные модули

def get_material_types_keyboard(material_types, language):
    """
    Создает клавиатуру с типами материалов.

    Args:
        material_types (list): Список доступных типов материалов.
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура с типами материалов.
    """
    from app.keyboards.dynamic_kb import get_material_types_keyboard
    return get_material_types_keyboard(material_types, language)


def get_semester_keyboard(material_type, semesters, language):
    """
    Создает клавиатуру с семестрами.

    Args:
        material_type (str): Тип материала.
        semesters (list): Список доступных семестров.
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура с семестрами.
    """
    from app.keyboards.dynamic_kb import get_semesters_keyboard
    return get_semesters_keyboard(material_type, semesters, language)


def get_materials_keyboard(material_type, semester, materials, language):
    """
    Создает клавиатуру с материалами.

    Args:
        material_type (str): Тип материала.
        semester (str): Выбранный семестр.
        materials (list): Список доступных материалов.
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура с материалами.
    """
    from app.keyboards.dynamic_kb import get_materials_keyboard
    return get_materials_keyboard(material_type, semester, materials, language)
