"""
Модуль обработчиков для основного меню бота.
Содержит обработчики для навигации по главным разделам.
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
from app.keyboards.schedule_kb import get_schedule_keyboard
from app.services.user_service import UserService
from app.utils.helpers import get_text

# Создаем роутер для основного меню
main_menu_router = Router()

# Сервис для работы с данными пользователей
user_service = UserService()


@main_menu_router.message(Command("menu"))
async def cmd_main_menu(message: Message, state: FSMContext):
    """
    Обработчик команды /menu.
    Возвращает пользователя в основное меню.

    Args:
        message (Message): Сообщение с командой.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = message.from_user.id

    # Обновляем время последней активности
    await user_service.register_user_activity(user_id)

    # Устанавливаем состояние основного меню
    await state.set_state(UserStates.main_menu)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем текст для основного меню
    main_menu_text = get_text(language, "main_menu_text")

    # Отправляем сообщение с клавиатурой основного меню
    await message.answer(
        main_menu_text,
        reply_markup=get_main_menu_keyboard(language)
    )

    logger.info(f"Пользователь {user_id} вернулся в основное меню")


@main_menu_router.callback_query(F.data == "main_menu")
async def process_main_menu_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик возврата в основное меню через callback.

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Обновляем время последней активности
    await user_service.register_user_activity(user_id)

    # Устанавливаем состояние основного меню
    await state.set_state(UserStates.main_menu)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем текст для основного меню
    main_menu_text = get_text(language, "main_menu_text")

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение, показывая основное меню
    await callback.message.edit_text(
        main_menu_text,
        reply_markup=get_main_menu_keyboard(language)
    )

    logger.info(f"Пользователь {user_id} вернулся в основное меню через callback")


@main_menu_router.callback_query(F.data == "profile")
async def process_profile(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки 'Личный кабинет'.
    Переводит пользователя в раздел личного кабинета.

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Обновляем время последней активности
    await user_service.register_user_activity(user_id)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем текст для личного кабинета
    profile_text = get_text(language, "profile_text")

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # В личном кабинете (домашней странице) пользователю предлагается выбрать факультет
    # Поэтому здесь мы перенаправляем на обработчик выбора факультета
    # Редактируем сообщение с информацией о личном кабинете
    await callback.message.edit_text(
        profile_text,
        reply_markup=get_faculty_selection_keyboard(language)
    )

    logger.info(f"Пользователь {user_id} перешел в личный кабинет")


@main_menu_router.callback_query(F.data == "learning_center")
async def process_learning_center(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки 'Центр обучения'.
    Переводит пользователя в раздел центра обучения.

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

    logger.info(f"Пользователь {user_id} перешел в центр обучения")


@main_menu_router.callback_query(F.data == "schedule")
async def process_schedule(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки 'Расписание'.
    Переводит пользователя в раздел расписания.

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

    logger.info(f"Пользователь {user_id} перешел в раздел расписания")


@main_menu_router.callback_query(F.data == "channel")
async def process_channel(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки 'Наш канал'.
    Отправляет пользователю ссылку на канал.

    Args:
        callback (CallbackQuery): Callback-запрос.
        state (FSMContext): Контекст состояния FSM.
    """
    user_id = callback.from_user.id

    # Обновляем время последней активности
    await user_service.register_user_activity(user_id)

    # Получаем язык пользователя
    language = await user_service.get_user_language(user_id) or settings.LANGUAGE_DEFAULT

    # Получаем текст для сообщения о канале
    channel_text = get_text(language, "channel_text").format(channel_link=settings.CHANNEL_LINK)

    # Отвечаем на callback и перенаправляем на канал
    await callback.answer("Переход на канал", url=settings.CHANNEL_LINK)

    logger.info(f"Пользователь {user_id} перешел на канал")


# Функция для генерации клавиатуры выбора факультета должна быть определена
# в соответствующем модуле, например, profile.py или faculty.py
# Здесь она добавлена как заглушка:
def get_faculty_selection_keyboard(language):
    """
    Заглушка для функции получения клавиатуры выбора факультета.
    Должна быть определена в соответствующем модуле.

    Args:
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура выбора факультета.
    """
    # Это заглушка, реальный код должен быть в соответствующем модуле
    from app.keyboards.faculty_kb import get_faculty_keyboard
    return get_faculty_keyboard(language)
