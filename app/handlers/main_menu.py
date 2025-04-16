"""
Модуль обработчиков для основного меню бота.
Содержит обработчики для навигации по главным разделам.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.config import get_config
from app.handlers.start import UserStates
from app.keyboards.learning_center_kb import get_learning_center_keyboard
from app.keyboards.main_menu_kb import get_main_menu_keyboard
from app.keyboards.faculty_kb import get_faculty_keyboard
from app.keyboards.schedule_kb import get_schedule_keyboard
from app.services.user_activity import UserActivityTracker
from app.utils.helpers import get_text

# Получаем конфигурацию
config = get_config()

# Создаем роутер для основного меню
main_menu_router = Router()

# Инициализация трекера активности
user_activity = UserActivityTracker()

@main_menu_router.message(Command("menu"))
async def cmd_main_menu(message: Message, state: FSMContext):
    """
    Обработчик команды /menu.
    Возвращает пользователя в основное меню.
    """
    user_id = message.from_user.id

    # Обновляем активность пользователя
    user_activity.update_activity(user_id)

    # Устанавливаем состояние основного меню
    await state.set_state(UserStates.main_menu)

    # Получаем язык пользователя
    language = user_activity.get_user_activity(user_id).get('language', config.LANGUAGE_DEFAULT)

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
    """
    user_id = callback.from_user.id

    # Обновляем активность пользователя
    user_activity.update_activity(user_id)

    # Устанавливаем состояние основного меню
    await state.set_state(UserStates.main_menu)

    # Получаем язык пользователя
    language = user_activity.get_user_activity(user_id).get('language', config.LANGUAGE_DEFAULT)

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
    """
    user_id = callback.from_user.id

    # Обновляем активность пользователя
    user_activity.update_activity(user_id)

    # Получаем язык пользователя
    language = user_activity.get_user_activity(user_id).get('language', config.LANGUAGE_DEFAULT)

    # Получаем текст для личного кабинета
    profile_text = get_text(language, "profile_text")

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение с информацией о личном кабинете
    await callback.message.edit_text(
        profile_text,
        reply_markup=get_faculty_keyboard(language)
    )

    logger.info(f"Пользователь {user_id} перешел в личный кабинет")

@main_menu_router.callback_query(F.data == "learning_center")
async def process_learning_center(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки 'Центр обучения'.
    """
    user_id = callback.from_user.id

    # Обновляем активность пользователя
    user_activity.update_activity(user_id)

    # Получаем язык пользователя
    language = user_activity.get_user_activity(user_id).get('language', config.LANGUAGE_DEFAULT)

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
    """
    user_id = callback.from_user.id

    # Обновляем активность пользователя
    user_activity.update_activity(user_id)

    # Получаем язык пользователя
    language = user_activity.get_user_activity(user_id).get('language', config.LANGUAGE_DEFAULT)

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
    """Обработчик кнопки 'Наш канал'."""
    user_id = callback.from_user.id
    user_activity.update_activity(user_id)

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)

    try:
        # 1. Сначала отвечаем на callback
        await callback.answer()

        # 2. Затем отправляем сообщение с кнопкой
        await callback.message.answer(
            get_text(language, "channel_text").format(channel_link=str(config.CHANNEL_LINK)),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=get_text(language, "open_channel_button"),
                            url=str(config.CHANNEL_LINK)  # Преобразуем URL в строку
                        )
                    ]
                ]
            )
        )

        logger.info(f"User {user_id} requested channel link")
    except Exception as e:
        logger.error(f"Error processing channel request: {e}")
        await callback.answer(get_text(language, "error_occurred"))

