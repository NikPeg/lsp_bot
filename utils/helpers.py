import os
from typing import Optional, List, Tuple

def get_parent_path(path: str) -> Optional[str]:
    """
    Получает родительский путь для заданного пути

    Аргументы:
        path (str): Текущий путь

    Возвращает:
        Optional[str]: Родительский путь или None, если путь корневой
    """
    parent = os.path.dirname(path)
    if parent == path or not parent:
        return None
    return parent

def format_path(path: str) -> str:
    """
    Форматирует путь для отображения пользователю

    Аргументы:
        path (str): Путь в файловой системе

    Возвращает:
        str: Отформатированный путь
    """
    # Удаляем начальную часть пути, чтобы показать только относительную часть
    base_dirs = ["data/materials/", "data/materials", "data/", "data"]
    for base_dir in base_dirs:
        if path.startswith(base_dir):
            path = path[len(base_dir):].lstrip('/')
            break

    # Заменяем слэши на стрелки для более наглядного отображения
    return path.replace('/', ' → ') if path else "/"

def parse_callback_data(callback_data: str) -> Tuple[str, str]:
    """
    Разбирает данные обратного вызова на тип и значение

    Аргументы:
        callback_data (str): Строка обратного вызова (например, "navigate:path/to/dir")

    Возвращает:
        Tuple[str, str]: Кортеж (тип, значение)
    """
    parts = callback_data.split(':', 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return parts[0], ""

def get_file_extension(filename: str) -> str:
    """
    Получает расширение файла

    Аргументы:
        filename (str): Имя файла

    Возвращает:
        str: Расширение файла (без точки)
    """
    return os.path.splitext(filename)[1][1:].lower()

def is_image_file(filename: str) -> bool:
    """
    Проверяет, является ли файл изображением

    Аргументы:
        filename (str): Имя файла

    Возвращает:
        bool: True, если файл является изображением
    """
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']
    return get_file_extension(filename) in image_extensions

def split_long_message(text: str, max_length: int = 4096) -> List[str]:
    """
    Разбивает длинное сообщение на части, если оно превышает ограничение Telegram

    Аргументы:
        text (str): Исходный текст
        max_length (int): Максимальная длина сообщения

    Возвращает:
        List[str]: Список частей сообщения
    """
    if len(text) <= max_length:
        return [text]

    parts = []
    for i in range(0, len(text), max_length):
        parts.append(text[i:i + max_length])

    return parts
