from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.text_manager import get_text
from utils.emoji import add_emoji_to_text

def get_schedule_keyboard(language: str) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для выбора типа расписания

    Аргументы:
        language (str): Код языка (ru, en, ar)

    Возвращает:
        InlineKeyboardMarkup: Клавиатура с кнопками типов расписаний
    """
    # Создаем билдер для клавиатуры
    builder = InlineKeyboardBuilder()

    # Получаем переведенные тексты для кнопок
    deanery_text = add_emoji_to_text("🏢", get_text(language, "deanery_button"))
    sports_doctor_text = add_emoji_to_text("⚕️", get_text(language, "sports_doctor_button"))
    libraries_text = add_emoji_to_text("📚", get_text(language, "libraries_button"))
    pass_making_text = add_emoji_to_text("🪪", get_text(language, "pass_making_button"))
    practice_text = add_emoji_to_text("👨‍⚕️", get_text(language, "practice_button"))

    # Добавляем кнопки с переведенными текстами (по 2 в ряд где возможно)
    builder.row(
        InlineKeyboardButton(text=deanery_text, callback_data="schedule:deanery"),
        InlineKeyboardButton(text=sports_doctor_text, callback_data="schedule:sports_doctor")
    )

    builder.row(
        InlineKeyboardButton(text=libraries_text, callback_data="schedule:library"),
        InlineKeyboardButton(text=pass_making_text, callback_data="schedule:pass_making")
    )

    builder.row(
        InlineKeyboardButton(text=practice_text, callback_data="schedule:practice")
    )

    # Добавляем кнопку для возврата в главное меню
    back_text = add_emoji_to_text("🔙", get_text(language, "back_to_main_menu"))
    builder.row(
        InlineKeyboardButton(text=back_text, callback_data="back_to_main")
    )

    return builder.as_markup()
