from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.text_manager import get_text
from services.file_manager import get_directories, get_files
from utils.emoji import add_emoji_to_text
import os

async def get_navigation_keyboard(
        language: str,
        current_path: str,
        parent_path: str = None
) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для навигации по файловой системе

    Аргументы:
        language (str): Код языка (ru, en, ar)
        current_path (str): Текущий путь в файловой системе
        parent_path (str, optional): Родительский путь для кнопки "Назад"

    Возвращает:
        InlineKeyboardMarkup: Клавиатура с кнопками для навигации
    """
    keyboard = InlineKeyboardMarkup(row_width=1)

    # Получаем список папок в текущей директории
    directories = await get_directories(current_path)

    # Добавляем кнопку для каждой папки
    for directory in directories:
        dir_path = os.path.join(current_path, directory)
        dir_name = directory

        # Пытаемся найти перевод для названия папки (если есть)
        dir_text = get_text(language, f"dir_{dir_name.replace(' ', '_').lower()}", default=dir_name)
        dir_text = add_emoji_to_text("📁", dir_text)

        keyboard.add(InlineKeyboardButton(
            text=dir_text,
            callback_data=f"navigate:{dir_path}"
        ))

    # Получаем список файлов в текущей директории
    files = await get_files(current_path)

    # Добавляем кнопку для каждого файла
    for file in files:
        file_path = os.path.join(current_path, file)
        file_name = os.path.splitext(file)[0]  # Имя файла без расширения

        # Пытаемся найти перевод для названия файла (если есть)
        file_text = get_text(language, f"file_{file_name.replace(' ', '_').lower()}", default=file)
        file_text = add_emoji_to_text("📄", file_text)

        keyboard.add(InlineKeyboardButton(
            text=file_text,
            callback_data=f"download:{file_path}"
        ))

    # Добавляем кнопку "Назад", если есть родительский путь
    if parent_path:
        back_text = add_emoji_to_text("🔙", get_text(language, "back_button"))
        keyboard.add(InlineKeyboardButton(
            text=back_text,
            callback_data=f"navigate:{parent_path}"
        ))
    else:
        # Если это корневая директория, добавляем кнопку для возврата в главное меню
        back_to_main_text = add_emoji_to_text("🏠", get_text(language, "back_to_main_menu"))
        keyboard.add(InlineKeyboardButton(
            text=back_to_main_text,
            callback_data="back_to_main"
        ))

    return keyboard
