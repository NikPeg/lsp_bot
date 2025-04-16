"""
Модуль обработчиков для раздела расписания.
Предоставляет изображения с расписанием различных подразделений.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile
from loguru import logger
from pathlib import Path

from app.config import get_config
from app.keyboards.main_menu_kb import get_main_menu_keyboard
from app.keyboards.schedule_kb import get_schedule_keyboard
from app.services.user_activity import UserActivityTracker
from app.utils.helpers import get_text

# Получаем конфигурацию
config = get_config()

# Создаем роутер для расписания
schedule_router = Router()

# Инициализация сервиса
user_activity = UserActivityTracker()

# Список доступных расписаний
SCHEDULE_TYPES = {
    "deanery": {
        "image": "deanery.png",
        "text_key": "deanery_schedule_text"
    },
    "sports_doctor": {
        "image": "sports_doctor.png",
        "text_key": "sports_doctor_schedule_text"
    },
    "anatomy": {
        "image": "anatomy.png",
        "text_key": "anatomy_schedule_text"
    },
    "libraries": {
        "image": "libraries.png",
        "text_key": "libraries_schedule_text"
    },
    "pass_making": {
        "image": "pass_making.png",
        "text_key": "pass_making_schedule_text"
    },
    "practice": {
        "image": "practice.png",
        "text_key": "practice_schedule_text"
    },
    "departments": {
        "image": "departments.png",
        "text_key": "departments_schedule_text"
    }
}

@schedule_router.callback_query(F.data == "schedule")
async def show_schedule(callback: CallbackQuery, state: FSMContext):
    """Обработчик перехода в раздел расписания."""
    user_id = callback.from_user.id
    user_activity.update_activity(user_id)

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)

    await callback.answer()
    await callback.message.edit_text(
        get_text(language, "schedule_text"),
        reply_markup=get_schedule_keyboard(language)
    )
    logger.info(f"User {user_id} opened schedule section")

@schedule_router.callback_query(F.data.startswith("schedule_"))
async def handle_schedule_selection(callback: CallbackQuery, state: FSMContext):
    """Общий обработчик для всех типов расписаний."""
    user_id = callback.from_user.id
    schedule_type = callback.data.split('_', 1)[1]

    if schedule_type == "back":
        await schedule_back_to_main(callback, state)
        return

    if schedule_type not in SCHEDULE_TYPES:
        logger.warning(f"Unknown schedule type: {schedule_type}")
        return

    await show_schedule_image(
        callback,
        SCHEDULE_TYPES[schedule_type]["image"],
        SCHEDULE_TYPES[schedule_type]["text_key"]
    )


async def show_schedule_image(callback: CallbackQuery, image_filename: str, text_key: str):
    """Отправляет изображение с расписанием."""
    user_id = callback.from_user.id
    user_activity.update_activity(user_id)

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)

    image_path = Path(config.IMAGES_FOLDER) / "schedule" / image_filename
    schedule_description = get_text(language, text_key)

    await callback.answer()

    if not image_path.exists():
        await callback.message.answer(
            get_text(language, "image_not_found"),
            reply_markup=get_schedule_keyboard(language)
        )
        logger.error(f"Image not found: {image_path}")
        return

    try:
        # Создаем InputFile правильно
        photo = InputFile(image_path)

        await callback.message.answer_photo(
            photo=photo,
            caption=schedule_description,
            protect_content=True
        )

        # Кнопка возврата
        await callback.message.answer(
            get_text(language, "back_to_schedule"),
            reply_markup=get_schedule_keyboard(language)
        )

        logger.info(f"User {user_id} viewed schedule: {image_filename}")
    except Exception as e:
        logger.error(f"Error sending schedule image: {e}")
        await callback.message.answer(
            get_text(language, "error_sending_image"),
            reply_markup=get_schedule_keyboard(language)
        )


@schedule_router.callback_query(F.data == "schedule_back")
async def schedule_back_to_main(callback: CallbackQuery, state: FSMContext):
    """Обработчик возврата в главное меню."""
    user_id = callback.from_user.id
    user_activity.update_activity(user_id)

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)

    await callback.answer()
    await callback.message.edit_text(
        get_text(language, "main_menu_text"),
        reply_markup=get_main_menu_keyboard(language)
    )
    logger.info(f"User {user_id} returned to main menu from schedule")

@schedule_router.message(Command("schedule"))
async def cmd_schedule(message: Message, state: FSMContext):
    """Обработчик команды /schedule."""
    user_id = message.from_user.id
    user_activity.update_activity(user_id)

    user_data = user_activity.get_user_activity(user_id)
    language = user_data.get('language', config.LANGUAGE_DEFAULT)

    await message.answer(
        get_text(language, "schedule_text"),
        reply_markup=get_schedule_keyboard(language)
    )
    logger.info(f"User {user_id} opened schedule via command")
