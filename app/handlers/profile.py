"""
Модуль обработчиков для личного кабинета (выбор факультета).
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger

from app.config import settings
from app.keyboards.faculty_kb import get_faculty_keyboard
from app.keyboards.main_menu_kb import get_main_menu_keyboard
from app.services.file_system import FileSystemService
from app.services.user_service import UserService
from app.utils.helpers import get_text

# Создаем роутер для личного кабинета
profile_router = Router()

# Сервисы для работы с пользователями и файловой системой
user_service = UserService()
file_system_service = FileSystemService()


@profile_router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик перехода в личный кабинет.

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Обновляем время последней активности
    await user_service.register_user_activity(user_id)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем текущий выбранный факультет пользователя (если есть)
    current_faculty = await user_service.get_user_faculty(user_id)

    # Формируем текст в зависимости от того, выбран ли уже факультет
    if current_faculty:
        # Получаем название факультета на правильном языке
        faculty_name = get_faculty_name(current_faculty, language)
        profile_text = get_text(language, "profile_with_faculty").format(faculty=faculty_name)
    else:
        profile_text = get_text(language, "profile_no_faculty")

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Получаем клавиатуру с факультетами
    keyboard = get_faculty_keyboard(language)

    # Редактируем сообщение, предлагая выбрать факультет
    await callback.message.edit_text(
        profile_text,
        reply_markup=keyboard
    )

    logger.info(f"Пользователь {user_id} открыл личный кабинет")


@profile_router.callback_query(F.data.startswith("faculty_"))
async def process_faculty_selection(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора факультета.

    Args:
        callback (CallbackQuery): Callback-запрос с выбранным факультетом.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Извлекаем код факультета из данных callback
    selected_faculty = callback.data.split('_')[1]

    # Проверяем, что факультет существует
    faculties = await file_system_service.get_faculties()
    if selected_faculty not in faculties:
        await callback.answer(get_text(settings.LANGUAGE_DEFAULT, "faculty_not_found"))
        return

    # Сохраняем выбранный факультет
    await user_service.set_user_faculty(user_id, selected_faculty)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем название факультета на выбранном языке
    faculty_name = get_faculty_name(selected_faculty, language)

    # Формируем текст подтверждения выбора факультета
    confirmation_text = get_text(language, "faculty_selected").format(faculty=faculty_name)

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение, показывая подтверждение выбора
    await callback.message.edit_text(
        confirmation_text,
        reply_markup=get_main_menu_keyboard(language)
    )

    logger.info(f"Пользователь {user_id} выбрал факультет: {selected_faculty}")


@profile_router.message(Command("profile"))
async def cmd_profile(message: Message, state: FSMContext):
    """
    Обработчик команды /profile.
    Показывает информацию о личном кабинете и позволяет выбрать факультет.

    Args:
        message (Message): Сообщение с командой.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = message.from_user.id

    # Обновляем время последней активности
    await user_service.register_user_activity(user_id)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем текущий выбранный факультет пользователя (если есть)
    current_faculty = await user_service.get_user_faculty(user_id)

    # Формируем текст в зависимости от того, выбран ли уже факультет
    if current_faculty:
        # Получаем название факультета на правильном языке
        faculty_name = get_faculty_name(current_faculty, language)
        profile_text = get_text(language, "profile_with_faculty").format(faculty=faculty_name)
    else:
        profile_text = get_text(language, "profile_no_faculty")

    # Получаем клавиатуру с факультетами
    keyboard = get_faculty_keyboard(language)

    # Отправляем сообщение, предлагая выбрать факультет
    await message.answer(
        profile_text,
        reply_markup=keyboard
    )

    logger.info(f"Пользователь {user_id} открыл личный кабинет через команду")


def get_faculty_name(faculty_code, language):
    """
    Получает название факультета на нужном языке.

    Args:
        faculty_code (str): Код факультета.
        language (str): Код языка.

    Returns:
        str: Название факультета на указанном языке.
    """
    # Словарь с названиями факультетов на разных языках
    faculty_names = {
        "L": {
            "ru": settings.FACULTY_L_NAME,
            "en": "Faculty of Medicine",
            "ar": "كلية الطب"
        },
        "S": {
            "ru": settings.FACULTY_S_NAME,
            "en": "Faculty of Dentistry",
            "ar": "كلية طب الأسنان"
        },
        "P": {
            "ru": settings.FACULTY_P_NAME,
            "en": "Faculty of Pediatrics",
            "ar": "كلية طب الأطفال"
        }
    }

    # Получаем название или возвращаем код как запасной вариант
    return faculty_names.get(faculty_code, {}).get(language, faculty_code)
