import os
import asyncio
from typing import List, Optional

from config import MATERIALS_FOLDER

async def get_directories(path: str) -> List[str]:
    """
    Получает список подпапок в указанной директории

    Аргументы:
        path (str): Путь к директории

    Возвращает:
        List[str]: Список имен подпапок
    """
    try:
        # Запускаем синхронный код в отдельном потоке через ThreadPoolExecutor
        result = await asyncio.to_thread(_get_directories_sync, path)
        return result
    except Exception as e:
        print(f"Error getting directories: {e}")
        return []

def _get_directories_sync(path: str) -> List[str]:
    """
    Синхронная версия функции get_directories
    """
    if not os.path.exists(path) or not os.path.isdir(path):
        return []

    directories = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path) and not item.startswith('.'):
            directories.append(item)

    return sorted(directories)

async def get_files(path: str) -> List[str]:
    """
    Получает список файлов в указанной директории

    Аргументы:
        path (str): Путь к директории

    Возвращает:
        List[str]: Список имен файлов
    """
    try:
        # Запускаем синхронный код в отдельном потоке через ThreadPoolExecutor
        result = await asyncio.to_thread(_get_files_sync, path)
        return result
    except Exception as e:
        print(f"Error getting files: {e}")
        return []

def _get_files_sync(path: str) -> List[str]:
    """
    Синхронная версия функции get_files
    """
    if not os.path.exists(path) or not os.path.isdir(path):
        return []

    files = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path) and not item.startswith('.'):
            files.append(item)

    return sorted(files)

async def get_faculties() -> List[str]:
    """
    Получает список доступных факультетов

    Возвращает:
        List[str]: Список имен факультетов
    """
    return await get_directories(MATERIALS_FOLDER)

async def check_faculty_exists(faculty: str) -> bool:
    """
    Проверяет, существует ли факультет

    Аргументы:
        faculty (str): Имя факультета

    Возвращает:
        bool: True, если факультет существует
    """
    faculties = await get_faculties()
    return faculty in faculties

async def check_file_exists(file_path: str) -> bool:
    """
    Проверяет, существует ли файл

    Аргументы:
        file_path (str): Путь к файлу

    Возвращает:
        bool: True, если файл существует
    """
    try:
        result = await asyncio.to_thread(os.path.exists, file_path)
        return result and await asyncio.to_thread(os.path.isfile, file_path)
    except Exception as e:
        print(f"Error checking file existence: {e}")
        return False

async def get_file_info(file_path: str) -> Optional[dict]:
    """
    Получает информацию о файле

    Аргументы:
        file_path (str): Путь к файлу

    Возвращает:
        Optional[dict]: Словарь с информацией о файле или None, если файл не существует
    """
    if not await check_file_exists(file_path):
        return None

    try:
        # Получаем базовую информацию о файле
        filename = os.path.basename(file_path)
        extension = os.path.splitext(filename)[1][1:].lower()

        # Получаем размер файла (в байтах)
        file_size = await asyncio.to_thread(os.path.getsize, file_path)

        # Получаем дату модификации файла
        file_mtime = await asyncio.to_thread(os.path.getmtime, file_path)

        return {
            "name": filename,
            "path": file_path,
            "extension": extension,
            "size": file_size,
            "modified": file_mtime
        }
    except Exception as e:
        print(f"Error getting file info: {e}")
        return None
