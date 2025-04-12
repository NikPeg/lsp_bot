"""
Модуль для создания клавиатуры выбора языка.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.config import settings


def get_language_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора языка интерфейса.

    Returns:
        InlineKeyboardMarkup: Клавиатура выбора языка.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="🇷🇺 Русский",
                callback_data="language_ru"
            )
        ],
        [
            InlineKeyboardButton(
                text="🇬🇧 English",
                callback_data="language_en"
            )
        ],
        [
            InlineKeyboardButton(
                text="🇸🇦 العربية",
                callback_data="language_ar"
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_language_settings_keyboard(current_language: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру настроек языка с отметкой текущего выбранного языка.

    Args:
        current_language (str): Текущий выбранный язык пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура настроек языка.
    """
    # Создаем маркеры для отображения выбранного языка
    ru_marker = "✅ " if current_language == "ru" else ""
    en_marker = "✅ " if current_language == "en" else ""
    ar_marker = "✅ " if current_language == "ar" else ""

    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{ru_marker}🇷🇺 Русский",
                callback_data="language_ru"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{en_marker}🇬🇧 English",
                callback_data="language_en"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{ar_marker}🇸🇦 العربية",
                callback_data="language_ar"
            )
        ],
        [
            InlineKeyboardButton(
                text="Назад / Back / رجوع",
                callback_data="learning_center"
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
