from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.helpers import get_text

def get_faculty_keyboard(language: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора факультета.

    Args:
        language: Язык пользователя

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками выбора факультета
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text(language, "faculty_L_name"),
                    callback_data="faculty_L"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text(language, "faculty_S_name"),
                    callback_data="faculty_S"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text(language, "faculty_P_name"),
                    callback_data="faculty_P"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text(language, "back_to_main_menu"),
                    callback_data="main_menu"
                )
            ]
        ]
    )

    return keyboard
