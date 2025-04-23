from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
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
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    # Получаем переведенные тексты для кнопок
    profile_text = add_emoji_to_text("👤", get_text(language, "profile_button"))
    learning_text = add_emoji_to_text("📚", get_text(language, "learning_center_button"))
    schedule_text = add_emoji_to_text("📆", get_text(language, "schedule_button"))
    channel_text = add_emoji_to_text("📢", get_text(language, "channel_button"))

    # Добавляем кнопки с переведенными текстами
    keyboard.add(
        KeyboardButton(profile_text),
        KeyboardButton(learning_text),
        KeyboardButton(schedule_text),
        KeyboardButton(channel_text)
    )

    return keyboard
