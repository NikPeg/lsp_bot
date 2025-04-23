import json
import os
from typing import Dict, Any, Optional

from config import TEXTS_DIR

# Кэш для хранения загруженных файлов переводов
_translations_cache = {}

def _load_language_file(language: str) -> Dict[str, Any]:
    """
    Загружает файл с переводами для указанного языка

    Аргументы:
        language (str): Код языка (ru, en, ar)

    Возвращает:
        Dict[str, Any]: Словарь с переводами
    """
    # Если переводы уже загружены в кэш, возвращаем их
    if language in _translations_cache:
        return _translations_cache[language]

    try:
        # Формируем путь к файлу с переводами
        file_path = os.path.join(TEXTS_DIR, f"{language}.json")

        # Проверяем существование файла
        if not os.path.exists(file_path):
            print(f"Translation file for language '{language}' not found: {file_path}")
            return {}

        # Загружаем и разбираем JSON
        with open(file_path, 'r', encoding='utf-8') as file:
            translations = json.load(file)

        # Сохраняем переводы в кэш
        _translations_cache[language] = translations

        return translations

    except Exception as e:
        print(f"Error loading translations for '{language}': {e}")
        return {}

def get_text(language: str, key: str, default: Optional[str] = None, **kwargs) -> str:
    """
    Получает перевод текста по ключу для указанного языка

    Аргументы:
        language (str): Код языка (ru, en, ar)
        key (str): Ключ для поиска перевода
        default (Optional[str]): Текст по умолчанию, если перевод не найден
        **kwargs: Переменные для форматирования текста

    Возвращает:
        str: Переведенный текст
    """
    # Загружаем переводы для указанного языка
    translations = _load_language_file(language)

    # Получаем текст по ключу
    text = translations.get(key)

    # Если текст не найден и указан язык отличный от английского,
    # пробуем получить текст на английском
    if text is None and language != 'en':
        en_translations = _load_language_file('en')
        text = en_translations.get(key)

    # Если текст всё еще не найден, используем значение по умолчанию или ключ
    if text is None:
        text = default if default is not None else key

    # Форматируем текст, если указаны аргументы для форматирования
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError as e:
            print(f"Error formatting text '{key}': Missing key {e}")
        except Exception as e:
            print(f"Error formatting text '{key}': {e}")

    return text

def get_all_texts(language: str) -> Dict[str, str]:
    """
    Получает все переводы для указанного языка

    Аргументы:
        language (str): Код языка (ru, en, ar)

    Возвращает:
        Dict[str, str]: Словарь со всеми переводами
    """
    return _load_language_file(language)
