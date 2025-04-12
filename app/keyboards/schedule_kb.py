"""
Модуль для создания клавиатуры раздела расписания.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.utils.helpers import get_text


def get_schedule_keyboard(language: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для раздела расписания.

    Args:
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура расписания.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text=get_text(language, "deanery_button"),
                callback_data="schedule_deanery"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "sports_doctor_button"),
                callback_data="schedule_sports_doctor"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "anatomy_button"),
                callback_data="schedule_anatomy"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "libraries_button"),
                callback_data="schedule_libraries"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "pass_making_button"),
                callback_data="schedule_pass_making"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "practice_button"),
                callback_data="schedule_practice"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "departments_button"),
                callback_data="schedule_departments"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, "back_button"),
                callback_data="schedule_back"
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
