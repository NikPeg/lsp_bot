from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_language_keyboard() -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для выбора языка

    Возвращает:
        InlineKeyboardMarkup: Клавиатура с кнопками для выбора языка
    """
    # Создаем билдер для клавиатуры
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки для выбора языка
    builder.row(
        InlineKeyboardButton(text="🇬🇧 English", callback_data="language:en")
    )
    builder.row(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="language:ru")
    )
    builder.row(
        InlineKeyboardButton(text="🇸🇦 العربية", callback_data="language:ar")
    )

    # Строим и возвращаем клавиатуру
    return builder.as_markup()
