import json
from pathlib import Path
from typing import Dict, Optional
from loguru import logger

from ..config import get_config

config = get_config()

# Загрузка текстовых ресурсов
_texts_cache: Dict[str, Dict[str, str]] = {}

def load_texts(language: str) -> Dict[str, str]:
    """Загружает тексты для указанного языка"""
    if language in _texts_cache:
        return _texts_cache[language]

    try:
        file_path = Path(f"data/texts/{language}.json")
        if not file_path.exists():
            logger.warning(f"Text file not found for language: {language}")
            return {}

        with open(file_path, 'r', encoding='utf-8') as f:
            texts = json.load(f)
            _texts_cache[language] = texts
            return texts

    except Exception as e:
        logger.error(f"Error loading texts for {language}: {e}")
        return {}

def get_text(language: str, key: str, default: Optional[str] = None) -> str:
    """
    Получает текст по ключу для указанного языка.

    Args:
        language: Код языка (ru, en, ar)
        key: Ключ текста
        default: Значение по умолчанию, если текст не найден

    Returns:
        Запрошенный текст или значение по умолчанию
    """
    if language not in ["ru", "en", "ar"]:
        language = config.LANGUAGE_DEFAULT
        logger.warning(f"Invalid language code, using default: {language}")

    texts = load_texts(language)
    text = texts.get(key, default)

    if text is None:
        logger.error(f"Text not found for key '{key}' in language '{language}'")
        return f"[{key}]"  # Возвращаем ключ в скобках, если текст не найден

    return text

def get_schedule_image_path(image_name: str) -> Path:
    """Возвращает полный путь к изображению расписания"""
    return config.IMAGES_FOLDER / "schedule" / image_name
