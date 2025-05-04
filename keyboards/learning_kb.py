from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.text_manager import get_text
from services.file_manager import get_directories, get_files
from utils.emoji import add_emoji_to_text
import os
import hashlib
import re

# Словарь для хранения соответствия хешей и путей
_path_cache = {}

def get_path_id(path: str) -> str:
    """
    Создает короткий идентификатор для пути

    Аргументы:
        path (str): Полный путь к файлу или директории

    Возвращает:
        str: Короткий идентификатор пути
    """
    # Создаем хеш пути
    path_hash = hashlib.md5(path.encode()).hexdigest()[:8]

    # Сохраняем соответствие в кэше
    _path_cache[path_hash] = path

    return path_hash

def get_path_by_id(path_id: str) -> str:
    """
    Получает полный путь по идентификатору

    Аргументы:
        path_id (str): Идентификатор пути

    Возвращает:
        str: Полный путь или пустую строку, если идентификатор не найден
    """
    return _path_cache.get(path_id, "")

def smart_sort_key(text):
    """
    Умная функция сортировки, которая сначала ищет и сортирует по числу,
    а затем по алфавиту.

    Аргументы:
        text (str): Текст для сортировки

    Возвращает:
        tuple: Кортеж (есть_ли_число, число_или_0, текст_в_нижнем_регистре)
    """
    # Ищем числа в тексте
    numbers = re.findall(r'\d+', text)

    # Если найдено хотя бы одно число, используем первое для сортировки
    if numbers:
        # Преобразуем найденное число в int
        number = int(numbers[0])
        # Возвращаем кортеж для сортировки (True = есть число, число, текст в нижнем регистре)
        return (True, number, text.lower())
    else:
        # Если числа нет, помещаем элемент после тех, где есть числа
        # (False = нет числа, 0 = нулевое число, текст в нижнем регистре)
        return (False, 0, text.lower())

async def get_navigation_keyboard(
        language: str,
        current_path: str,
        parent_path: str = None
) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для навигации по файловой системе с умной сортировкой

    Аргументы:
        language (str): Код языка (ru, en, ar)
        current_path (str): Текущий путь в файловой системе
        parent_path (str, optional): Родительский путь для кнопки "Назад"

    Возвращает:
        InlineKeyboardMarkup: Клавиатура с кнопками для навигации
    """
    # Создаем билдер для клавиатуры
    builder = InlineKeyboardBuilder()

    # Получаем список папок в текущей директории
    directories = await get_directories(current_path)

    # Создаем список пар (отображаемое имя, путь) для сортировки папок
    dir_pairs = []
    for directory in directories:
        dir_path = os.path.join(current_path, directory)
        dir_name = directory

        # Пытаемся найти перевод для названия директории
        dir_key = f"dir_{dir_name.replace(' ', '_').lower()}"
        dir_text = get_text(language, dir_key, default=dir_name)

        dir_pairs.append((dir_text, dir_path, dir_name))

    # Умная сортировка папок
    dir_pairs.sort(key=lambda x: smart_sort_key(x[0]))

    # Добавляем кнопки папок в отсортированном порядке
    for dir_text, dir_path, dir_name in dir_pairs:
        # Создаем короткий идентификатор для пути
        dir_path_id = get_path_id(dir_path)

        button_text = add_emoji_to_text("📁", dir_text)
        builder.row(
            InlineKeyboardButton(text=button_text, callback_data=f"nav:{dir_path_id}")
        )

    # Получаем список файлов в текущей директории
    files = await get_files(current_path)

    # Создаем список пар (отображаемое имя, путь) для сортировки файлов
    file_pairs = []
    for file in files:
        file_path = os.path.join(current_path, file)
        file_name = os.path.splitext(file)[0]  # Имя файла без расширения

        # Пытаемся найти перевод для названия файла (если есть)
        file_key = f"file_{file_name.replace(' ', '_').lower()}"
        file_text = get_text(language, file_key, default=file)

        file_pairs.append((file_text, file_path, file))

    # Умная сортировка файлов
    file_pairs.sort(key=lambda x: smart_sort_key(x[0]))

    # Добавляем кнопки файлов в отсортированном порядке
    for file_text, file_path, file in file_pairs:
        # Создаем короткий идентификатор для пути к файлу
        file_path_id = get_path_id(file_path)

        button_text = add_emoji_to_text("📄", file_text)
        builder.row(
            InlineKeyboardButton(text=button_text, callback_data=f"dl:{file_path_id}")
        )

    # Добавляем кнопку "Назад", если есть родительский путь
    if parent_path:
        # Создаем короткий идентификатор для родительского пути
        parent_path_id = get_path_id(parent_path)

        back_text = add_emoji_to_text("🔙", get_text(language, "back_button"))
        builder.row(
            InlineKeyboardButton(text=back_text, callback_data=f"nav:{parent_path_id}")
        )
    else:
        # Если это корневая директория, добавляем кнопку для возврата в главное меню
        back_to_main_text = add_emoji_to_text("🏠", get_text(language, "back_to_main_menu"))
        builder.row(
            InlineKeyboardButton(text=back_to_main_text, callback_data="back_to_main")
        )

    return builder.as_markup()
