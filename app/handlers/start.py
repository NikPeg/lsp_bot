"""
Модуль обработчиков для команды старта и выбора языка в боте.
"""

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from ..config import get_config
from app.keyboards.language_kb import get_language_keyboard
from app.keyboards.main_menu_kb import get_main_menu_keyboard
from app.services.user_service import UserService
from app.utils.helpers import get_text

# Получаем конфигурацию
config = get_config()

# Создаем роутер для команды старта и выбора языка
start_router = Router()

# Состояния для FSM
class UserStates(StatesGroup):
    """Класс состояний пользователя в боте."""
    language_selection = State()  # Состояние выбора языка
    main_menu = State()  # Состояние основного меню

# Сервис для работы с данными пользователей
user_service = UserService()

# Доступные языки
AVAILABLE_LANGUAGES = ["ru", "en", "ar"]

@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    Обработчик команды /start.
    Приветствует пользователя и предлагает выбрать язык.
    """
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name

    # Регистрируем пользователя или обновляем время последней активности
    await user_service.register_user_activity(user_id)

    logger.info(f"Пользователь {user_id} ({user_full_name}) запустил бота")

    # Получаем текущий язык пользователя или устанавливаем по умолчанию
    current_language = await user_service.get_user_language(user_id) or config.LANGUAGE_DEFAULT

    # Устанавливаем состояние выбора языка
    await state.set_state(UserStates.language_selection)

    # Создаем приветственное сообщение на трех языках
    welcome_message = (
        "🇷🇺 Добро пожаловать в ЛСП бот! Выберите язык интерфейса.\n\n"
        "🇬🇧 Welcome to LSP bot! Please select interface language.\n\n"
        "🇸🇦 مرحبًا بك في بوت LSP! يرجى اختيار لغة الواجهة."
    )

    # Отправляем сообщение с клавиатурой выбора языка
    await message.answer(
        welcome_message,
        reply_markup=get_language_keyboard()
    )

@start_router.callback_query(F.data.startswith("language_"))
async def process_language_selection(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора языка.
    """
    # Извлекаем код языка из данных callback
    selected_language = callback.data.split('_')[1]
    user_id = callback.from_user.id

    # Проверяем, что язык допустимый
    if selected_language not in AVAILABLE_LANGUAGES:
        await callback.answer("Язык не поддерживается / Language is not supported / اللغة غير مدعومة")
        return

    # Сохраняем выбранный язык
    await user_service.set_user_language(user_id, selected_language)

    # Устанавливаем состояние основного меню
    await state.set_state(UserStates.main_menu)

    # Получаем текст на выбранном языке
    welcome_text = get_text(selected_language, "welcome_text")

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback.answer()

    # Редактируем сообщение, показывая основное меню
    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(selected_language)
    )

    logger.info(f"Пользователь {user_id} выбрал язык: {selected_language}")

@start_router.message(Command("language"))
async def cmd_change_language(message: Message, state: FSMContext):
    """
    Обработчик команды /language для смены языка.
    """
    user_id = message.from_user.id

    # Обновляем время последней активности
    await user_service.register_user_activity(user_id)

    # Устанавливаем состояние выбора языка
    await state.set_state(UserStates.language_selection)

    # Получаем текущий язык пользователя
    current_language = await user_service.get_user_language(user_id) or config.LANGUAGE_DEFAULT

    # Получаем текст на текущем языке
    language_selection_text = get_text(current_language, "language_selection")

    # Отправляем сообщение с клавиатурой выбора языка
    await message.answer(
        language_selection_text,
        reply_markup=get_language_keyboard()
    )

    logger.info(f"Пользователь {user_id} запросил смену языка")
