"""
Модуль для создания клавиатуры центра обучения.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.utils.helpers import get_text


def get_learning_center_keyboard(language: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для раздела центра обучения.

    Args:
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура центра обучения.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text=get_text(language, "study_center_button"),
                callback_data="study_center"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "faculty_settings_button"),
                callback_data="faculty_settings"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "language_settings_button"),
                callback_data="language_settings"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "back_button"),
                callback_data="back_to_menu"
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
