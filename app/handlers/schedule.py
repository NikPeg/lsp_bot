"""
Модуль обработчиков для раздела расписания.
Предоставляет изображения с расписанием различных подразделений.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger
from pathlib import Path

from app.config import settings
from app.keyboards.main_menu_kb import get_main_menu_keyboard
from app.keyboards.schedule_kb import get_schedule_keyboard
from app.services.user_service import UserService
from app.utils.helpers import get_text

# Создаем роутер для расписания
schedule_router = Router()

# Сервис для работы с данными пользователей
user_service = UserService()


@schedule_router.callback_query(F.data == "schedule")
async def show_schedule(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик перехода в раздел расписания.

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Обновляем время последней активности
    await user_service.register_user_activity(user_id)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем текст для расписания
    schedule_text = get_text(language, "schedule_text")

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение, показывая меню расписания
    await callback.message.edit_text(
        schedule_text,
        reply_markup=get_schedule_keyboard(language)
    )

    logger.info(f"Пользователь {user_id} открыл раздел расписания")


@schedule_router.callback_query(F.data == "schedule_deanery")
async def show_deanery_schedule(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для отображения расписания деканата.

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    await show_schedule_image(callback, "deanery.jpg", "deanery_schedule_text")


@schedule_router.callback_query(F.data == "schedule_sports_doctor")
async def show_sports_doctor_schedule(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для отображения расписания спортивного врача.

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    await show_schedule_image(callback, "sports_doctor.jpg", "sports_doctor_schedule_text")


@schedule_router.callback_query(F.data == "schedule_anatomy")
async def show_anatomy_schedule(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для отображения расписания анатомички.

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    await show_schedule_image(callback, "anatomy.jpg", "anatomy_schedule_text")


@schedule_router.callback_query(F.data == "schedule_libraries")
async def show_libraries_schedule(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для отображения расписания библиотек.

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    await show_schedule_image(callback, "libraries.jpg", "libraries_schedule_text")


@schedule_router.callback_query(F.data == "schedule_pass_making")
async def show_pass_making_schedule(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для отображения расписания изготовления пропуска.

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    await show_schedule_image(callback, "pass_making.jpg", "pass_making_schedule_text")


@schedule_router.callback_query(F.data == "schedule_practice")
async def show_practice_schedule(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для отображения расписания производственной практики.

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    await show_schedule_image(callback, "practice.jpg", "practice_schedule_text")


@schedule_router.callback_query(F.data == "schedule_departments")
async def show_departments_schedule(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для отображения расписания дежурных по кафедрам.

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    await show_schedule_image(callback, "departments.jpg", "departments_schedule_text")


@schedule_router.callback_query(F.data == "schedule_back")
async def schedule_back_to_main(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Вернуться назад" из меню расписания.

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

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение, возвращаясь в главное меню
    await callback.message.edit_text(
        main_menu_text,
        reply_markup=get_main_menu_keyboard(language)
    )

    logger.info(f"Пользователь {user_id} вернулся из расписания в главное меню")


@schedule_router.message(Command("schedule"))
async def cmd_schedule(message: Message, state: FSMContext):
    """
    Обработчик команды /schedule.
    Показывает меню расписания.

    Args:
        message (Message): Сообщение с командой.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = message.from_user.id

    # Обновляем время последней активности
    await user_service.register_user_activity(user_id)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем текст для расписания
    schedule_text = get_text(language, "schedule_text")

    # Отправляем сообщение с клавиатурой расписания
    await message.answer(
        schedule_text,
        reply_markup=get_schedule_keyboard(language)
    )

    logger.info(f"Пользователь {user_id} открыл расписание через команду")


async def show_schedule_image(callback: CallbackQuery, image_filename: str, text_key: str):
    """
    Вспомогательная функция для отображения изображения с расписанием.

    Args:
        callback (CallbackQuery): Callback-запрос.
        image_filename (str): Имя файла изображения.
        text_key (str): Ключ для получения текста описания.
    """
    user_id = callback.from_user.id

    # Обновляем время последней активности
    await user_service.register_user_activity(user_id)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем текст описания для данного расписания
    schedule_description = get_text(language, text_key)

    # Формируем путь к изображению
    image_path = settings.schedule_images_path / image_filename

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    if image_path.exists():
        # Отправляем изображение с расписанием
        with open(image_path, 'rb') as photo:
            await callback.message.answer_photo(
                photo=photo,
                caption=schedule_description,
                protect_content=True  # Запрет на пересылку
            )

        # Отправляем кнопку для возврата к расписанию
        await callback.message.answer(
            get_text(language, "back_to_schedule"),
            reply_markup=get_schedule_keyboard(language)
        )

        logger.info(f"Пользователь {user_id} просмотрел расписание: {image_filename}")
    else:
        # Если изображение не найдено
        image_not_found_text = get_text(language, "image_not_found")
        await callback.message.answer(
            image_not_found_text,
            reply_markup=get_schedule_keyboard(language)
        )
        logger.error(f"Изображение не найдено: {image_path}")
