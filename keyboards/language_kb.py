from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_language_keyboard() -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для выбора языка

    Возвращает:
        InlineKeyboardMarkup: Клавиатура с кнопками для выбора языка
    """
    keyboard = InlineKeyboardMarkup(row_width=1)

    # Добавляем кнопки для выбора языка
    keyboard.add(
        InlineKeyboardButton(text="🇬🇧 English", callback_data="language:en"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="language:ru"),
        InlineKeyboardButton(text="🇸🇦 العربية", callback_data="language:ar")
    )

    return keyboard
