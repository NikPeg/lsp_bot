"""
Модуль для создания клавиатуры основного меню.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.utils.helpers import get_text


def get_main_menu_keyboard(language: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру основного меню.

    Args:
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура основного меню.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text=get_text(language, "profile_button"),
                callback_data="profile"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "learning_center_button"),
                callback_data="learning_center"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "schedule_button"),
                callback_data="schedule"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "channel_button"),
                callback_data="channel"
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
