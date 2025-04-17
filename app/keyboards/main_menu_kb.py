"""
Модуль для создания клавиатуры основного меню.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.utils.helpers import get_text


def get_main_menu_keyboard(language: str) -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру основного меню с использованием ReplyKeyboardMarkup.

    Args:
        language (str): Код языка пользователя.

    Returns:
        ReplyKeyboardMarkup: Клавиатура основного меню.
    """
    # Добавляем эмодзи к названиям разделов
    profile_text = f"🏛️ {get_text(language, 'profile_button')}"
    learning_center_text = f"📚 {get_text(language, 'learning_center_button')}"
    schedule_text = f"📅 {get_text(language, 'schedule_button')}"
    channel_text = f"📣 {get_text(language, 'channel_button')}"

    # Создаем клавиатуру с кнопками, расположенными в две строки
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=profile_text),
                KeyboardButton(text=learning_center_text)
            ],
            [
                KeyboardButton(text=schedule_text),
                KeyboardButton(text=channel_text)
            ]
        ],
        resize_keyboard=True,  # Уменьшаем размер клавиатуры
        one_time_keyboard=False,  # Клавиатура не скрывается после нажатия
        input_field_placeholder="Выберите раздел"  # Подсказка в поле ввода
    )

    return keyboard
