from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.text_manager import get_text
from utils.emoji import add_emoji_to_text
from config import CHANNEL_LINK

def get_back_keyboard(language: str, callback_data: str = "back_to_main") -> InlineKeyboardMarkup:
    """
    Создает простую инлайн-клавиатуру только с кнопкой "Назад"

    Аргументы:
        language (str): Код языка (ru, en, ar)
        callback_data (str): Данные для обратного вызова при нажатии на кнопку

    Возвращает:
        InlineKeyboardMarkup: Клавиатура с кнопкой "Назад"
    """
    back_text = add_emoji_to_text("🔙", get_text(language, "back_button"))

    # Создаем клавиатуру через двумерный массив
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=back_text, callback_data=callback_data)]
    ])

    return keyboard

def get_channel_keyboard(language: str) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру с кнопкой для перехода в канал

    Аргументы:
        language (str): Код языка (ru, en, ar)

    Возвращает:
        InlineKeyboardMarkup: Клавиатура с кнопкой для канала и кнопкой "Назад"
    """
    # Создаем билдер для клавиатуры
    builder = InlineKeyboardBuilder()

    # Кнопка для перехода в канал
    channel_text = add_emoji_to_text("📢", get_text(language, "open_channel_button"))
    builder.row(
        InlineKeyboardButton(text=channel_text, url=CHANNEL_LINK)
    )

    # Кнопка "Назад"
    back_text = add_emoji_to_text("🔙", get_text(language, "back_to_main_menu"))
    builder.row(
        InlineKeyboardButton(text=back_text, callback_data="back_to_main")
    )

    return builder.as_markup()

def get_after_file_keyboard(language: str) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру, которая отображается после отправки файла

    Аргументы:
        language (str): Код языка (ru, en, ar)

    Возвращает:
        InlineKeyboardMarkup: Клавиатура с кнопкой "Назад"
    """
    # Кнопка для возврата к материалам
    back_text = add_emoji_to_text("🔙", get_text(language, "back_button"))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=back_text, callback_data="back_to_materials")]
    ])

    return keyboard
