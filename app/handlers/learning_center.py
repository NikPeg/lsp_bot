"""
Модуль обработчиков для центра обучения.
Содержит функционал для доступа к учебным материалам.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger

from app.config import settings
from app.handlers.start import UserStates
from app.keyboards.learning_center_kb import get_learning_center_keyboard
from app.keyboards.main_menu_kb import get_main_menu_keyboard
from app.services.file_system import FileSystemService
from app.services.user_service import UserService
from app.utils.helpers import get_text

# Создаем роутер для центра обучения
learning_center_router = Router()

# Сервисы для работы с пользователями и файловой системой
user_service = UserService()
file_system_service = FileSystemService()


@learning_center_router.callback_query(F.data == "learning_center")
async def show_learning_center(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик перехода в центр обучения.

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Обновляем время последней активности
    await user_service.register_user_activity(user_id)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем текст для центра обучения
    learning_center_text = get_text(language, "learning_center_text")

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение, показывая меню центра обучения
    await callback.message.edit_text(
        learning_center_text,
        reply_markup=get_learning_center_keyboard(language)
    )

    logger.info(f"Пользователь {user_id} открыл центр обучения")


@learning_center_router.callback_query(F.data == "study_center")
async def show_study_center(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик перехода в учебный центр.

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Обновляем время последней активности
    await user_service.register_user_activity(user_id)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем выбранный факультет пользователя
    faculty = await user_service.get_user_faculty(user_id)

    if not faculty:
        # Если факультет не выбран, предлагаем его выбрать
        faculty_selection_text = get_text(language, "please_select_faculty")
        await callback.answer()
        await callback.message.edit_text(
            faculty_selection_text,
            reply_markup=get_faculty_selection_keyboard(language)
        )
        logger.info(f"Пользователь {user_id} попытался открыть учебный центр без выбора факультета")
        return

    # Получаем список предметов для выбранного факультета
    subjects = await file_system_service.get_subjects(faculty)

    if not subjects:
        # Если предметы не найдены
        no_subjects_text = get_text(language, "no_subjects_found")
        await callback.answer(no_subjects_text)
        await callback.message.edit_text(
            no_subjects_text,
            reply_markup=get_learning_center_keyboard(language)
        )
        logger.warning(f"Не найдены предметы для факультета {faculty}")
        return

    # Получаем текст и клавиатуру для выбора предмета
    subject_selection_text = get_text(language, "select_subject")
    subject_keyboard = get_subject_keyboard(subjects, language)

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение, показывая список предметов
    await callback.message.edit_text(
        subject_selection_text,
        reply_markup=subject_keyboard
    )

    logger.info(f"Пользователь {user_id} открыл список предметов для факультета {faculty}")


@learning_center_router.callback_query(F.data.startswith("subject_"))
async def process_subject_selection(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора предмета.

    Args:
        callback (CallbackQuery): Callback-запрос с выбранным предметом.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Извлекаем название предмета из данных callback
    subject_name = callback.data.split('_', 1)[1]

    # Сохраняем выбранный предмет в состоянии пользователя
    await state.update_data(selected_subject=subject_name)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем выбранный факультет пользователя
    faculty = await user_service.get_user_faculty(user_id)

    # Получаем типы материалов для выбранного предмета
    material_types = await file_system_service.get_material_types(faculty, subject_name)

    if not material_types:
        # Если типы материалов не найдены
        no_materials_text = get_text(language, "no_materials_found")
        await callback.answer(no_materials_text)
        # Возвращаемся к выбору предмета
        subjects = await file_system_service.get_subjects(faculty)
        subject_selection_text = get_text(language, "select_subject")
        subject_keyboard = get_subject_keyboard(subjects, language)
        await callback.message.edit_text(
            subject_selection_text,
            reply_markup=subject_keyboard
        )
        logger.warning(f"Не найдены материалы для предмета {subject_name}")
        return

    # Получаем текст и клавиатуру для выбора типа материала
    material_type_text = get_text(language, "select_material_type")
    material_type_keyboard = get_material_type_keyboard(material_types, language)

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение, показывая типы материалов
    await callback.message.edit_text(
        material_type_text,
        reply_markup=material_type_keyboard
    )

    logger.info(f"Пользователь {user_id} выбрал предмет: {subject_name}")


@learning_center_router.callback_query(F.data.startswith("material_type_"))
async def process_material_type_selection(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора типа материала.

    Args:
        callback (CallbackQuery): Callback-запрос с выбранным типом материала.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Извлекаем тип материала из данных callback
    material_type = callback.data.split('_', 2)[2]

    # Получаем данные из состояния
    state_data = await state.get_data()
    subject_name = state_data.get("selected_subject")

    # Сохраняем выбранный тип материала в состоянии пользователя
    await state.update_data(selected_material_type=material_type)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем выбранный факультет пользователя
    faculty = await user_service.get_user_faculty(user_id)

    # Получаем семестры для выбранного типа материала
    semesters = await file_system_service.get_semesters(faculty, subject_name, material_type)

    if not semesters:
        # Если семестры не найдены
        no_semesters_text = get_text(language, "no_semesters_found")
        await callback.answer(no_semesters_text)
        # Возвращаемся к выбору типа материала
        material_types = await file_system_service.get_material_types(faculty, subject_name)
        material_type_text = get_text(language, "select_material_type")
        material_type_keyboard = get_material_type_keyboard(material_types, language)
        await callback.message.edit_text(
            material_type_text,
            reply_markup=material_type_keyboard
        )
        logger.warning(f"Не найдены семестры для типа материала {material_type}")
        return

    # Получаем текст и клавиатуру для выбора семестра
    semester_text = get_text(language, "select_semester")
    semester_keyboard = get_semester_keyboard(semesters, language)

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение, показывая семестры
    await callback.message.edit_text(
        semester_text,
        reply_markup=semester_keyboard
    )

    logger.info(f"Пользователь {user_id} выбрал тип материала: {material_type}")


@learning_center_router.callback_query(F.data.startswith("semester_"))
async def process_semester_selection(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора семестра.

    Args:
        callback (CallbackQuery): Callback-запрос с выбранным семестром.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Извлекаем семестр из данных callback
    semester = callback.data.split('_', 1)[1]

    # Получаем данные из состояния
    state_data = await state.get_data()
    subject_name = state_data.get("selected_subject")
    material_type = state_data.get("selected_material_type")

    # Сохраняем выбранный семестр в состоянии пользователя
    await state.update_data(selected_semester=semester)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем выбранный факультет пользователя
    faculty = await user_service.get_user_faculty(user_id)

    # Получаем материалы для выбранного семестра
    materials = await file_system_service.get_materials(faculty, subject_name, material_type, semester)

    if not materials:
        # Если материалы не найдены
        no_materials_text = get_text(language, "no_materials_found_in_semester")
        await callback.answer(no_materials_text)
        # Возвращаемся к выбору семестра
        semesters = await file_system_service.get_semesters(faculty, subject_name, material_type)
        semester_text = get_text(language, "select_semester")
        semester_keyboard = get_semester_keyboard(semesters, language)
        await callback.message.edit_text(
            semester_text,
            reply_markup=semester_keyboard
        )
        logger.warning(f"Не найдены материалы для семестра {semester}")
        return

    # Получаем текст и клавиатуру для выбора материала
    materials_text = get_text(language, "select_material")
    materials_keyboard = get_materials_keyboard(materials, language)

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение, показывая материалы
    await callback.message.edit_text(
        materials_text,
        reply_markup=materials_keyboard
    )

    logger.info(f"Пользователь {user_id} выбрал семестр: {semester}")


@learning_center_router.callback_query(F.data.startswith("material_"))
async def send_material(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик отправки выбранного материала.

    Args:
        callback (CallbackQuery): Callback-запрос с выбранным материалом.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Извлекаем название материала из данных callback
    material_name = callback.data.split('_', 1)[1]

    # Получаем данные из состояния
    state_data = await state.get_data()
    subject_name = state_data.get("selected_subject")
    material_type = state_data.get("selected_material_type")
    semester = state_data.get("selected_semester")

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем выбранный факультет пользователя
    faculty = await user_service.get_user_faculty(user_id)

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Получаем файл материала
    material_path = await file_system_service.get_material_path(
        faculty, subject_name, material_type, semester, material_name
    )

    if not material_path or not material_path.exists():
        # Если файл не найден
        file_not_found_text = get_text(language, "file_not_found")
        await callback.message.answer(file_not_found_text)
        logger.error(f"Файл не найден: {material_path}")
        return

    # Отправляем файл
    try:
        # Определяем тип файла для правильной отправки
        file_extension = material_path.suffix.lower()

        # Текст сообщения с описанием материала
        material_info_text = get_text(language, "material_info").format(
            subject=subject_name,
            type=get_material_type_name(material_type, language),
            semester=semester,
            name=material_name
        )

        # Отправляем информацию о материале
        await callback.message.answer(material_info_text)

        # Отправляем файл с защитой от пересылки
        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            # Отправляем как фото
            await callback.message.answer_photo(
                photo=open(material_path, 'rb'),
                caption=material_name,
                protect_content=True  # Запрет на пересылку
            )
        elif file_extension in ['.pdf', '.doc', '.docx', '.txt', '.ppt', '.pptx']:
            # Отправляем как документ
            await callback.message.answer_document(
                document=open(material_path, 'rb'),
                caption=material_name,
                protect_content=True  # Запрет на пересылку
            )
        else:
            # Отправляем как файл
            await callback.message.answer_document(
                document=open(material_path, 'rb'),
                caption=material_name,
                protect_content=True  # Запрет на пересылку
            )

        logger.info(f"Пользователь {user_id} получил материал: {material_name}")

        # Возвращаем пользователя к списку материалов
        materials = await file_system_service.get_materials(faculty, subject_name, material_type, semester)
        materials_text = get_text(language, "select_material")
        materials_keyboard = get_materials_keyboard(materials, language)

        await callback.message.answer(
            materials_text,
            reply_markup=materials_keyboard
        )

    except Exception as e:
        error_text = get_text(language, "error_sending_file")
        await callback.message.answer(error_text)
        logger.error(f"Ошибка при отправке файла {material_path}: {e}")


@learning_center_router.callback_query(F.data == "language_settings")
async def show_language_settings(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик перехода к настройкам языка.

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Обновляем время последней активности
    await user_service.register_user_activity(user_id)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем текст для выбора языка
    language_settings_text = get_text(language, "language_settings_text")

    # Устанавливаем состояние выбора языка
    await state.set_state(UserStates.language_selection)

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение, показывая настройки языка
    await callback.message.edit_text(
        language_settings_text,
        reply_markup=get_language_keyboard()
    )

    logger.info(f"Пользователь {user_id} открыл настройки языка")


@learning_center_router.callback_query(F.data == "back_to_menu")
async def hide_learning_center(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для скрытия раздела и возврата в главное меню.

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Обновляем время последней активности
    await user_service.register_user_activity(user_id)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем текст для главного меню
    main_menu_text = get_text(language, "main_menu_text")

    # Устанавливаем состояние основного меню
    await state.set_state(UserStates.main_menu)

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение, показывая главное меню
    await callback.message.edit_text(
        main_menu_text,
        reply_markup=get_main_menu_keyboard(language)
    )

    logger.info(f"Пользователь {user_id} вернулся в главное меню")


# Вспомогательные функции для генерации клавиатур
# В реальном проекте их лучше перенести в отдельные модули

def get_faculty_selection_keyboard(language):
    """
    Функция для получения клавиатуры выбора факультета.

    Args:
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура выбора факультета.
    """
    from app.keyboards.faculty_kb import get_faculty_keyboard
    return get_faculty_keyboard(language)


def get_subject_keyboard(subjects, language):
    """
    Функция для получения клавиатуры выбора предмета.

    Args:
        subjects (list): Список доступных предметов.
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура выбора предмета.
    """
    from app.keyboards.dynamic_kb import get_subjects_keyboard
    return get_subjects_keyboard(subjects, language)


def get_material_type_keyboard(material_types, language):
    """
    Функция для получения клавиатуры выбора типа материала.

    Args:
        material_types (list): Список доступных типов материалов.
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура выбора типа материала.
    """
    from app.keyboards.dynamic_kb import get_material_types_keyboard
    return get_material_types_keyboard(material_types, language)


def get_semester_keyboard(semesters, language):
    """
    Функция для получения клавиатуры выбора семестра.

    Args:
        semesters (list): Список доступных семестров.
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура выбора семестра.
    """
    from app.keyboards.dynamic_kb import get_semesters_keyboard
    return get_semesters_keyboard(semesters, language)


def get_materials_keyboard(materials, language):
    """
    Функция для получения клавиатуры выбора материала.

    Args:
        materials (list): Список доступных материалов.
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура выбора материала.
    """
    from app.keyboards.dynamic_kb import get_materials_keyboard
    return get_materials_keyboard(materials, language)


def get_material_type_name(material_type, language):
    """
    Возвращает название типа материала на указанном языке.

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
            "ru": "Экзаменационные материлы",
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


# Импортируем функцию для получения клавиатуры выбора языка
from app.keyboards.language_kb import get_language_keyboard
