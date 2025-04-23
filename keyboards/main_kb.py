from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from services.text_manager import get_text
from utils.emoji import add_emoji_to_text

def get_main_keyboard(language: str) -> ReplyKeyboardMarkup:
    """
    Создает основную клавиатуру главного меню с переведенными кнопками

    Аргументы:
        language (str): Код языка (ru, en, ar)

    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с основными пунктами меню
    """
    # Создаем билдер для клавиатуры
    builder = ReplyKeyboardBuilder()

    # Получаем переведенные тексты для кнопок
    profile_text = add_emoji_to_text("👤", get_text(language, "profile_button"))
    learning_text = add_emoji_to_text("📚", get_text(language, "learning_center_button"))
    schedule_text = add_emoji_to_text("📆", get_text(language, "schedule_button"))
    channel_text = add_emoji_to_text("📢", get_text(language, "channel_button"))

    # Добавляем кнопки в строки
    builder.row(
        KeyboardButton(text=profile_text),
        KeyboardButton(text=learning_text)
    )

    builder.row(
        KeyboardButton(text=schedule_text),
        KeyboardButton(text=channel_text)
    )

    # Настраиваем параметры клавиатуры
    return builder.as_markup(resize_keyboard=True)
