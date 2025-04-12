"""
Модуль utils - вспомогательные утилиты для бота.
Содержит функции для работы с текстами, изображениями и другие полезные инструменты.
"""

from .helpers import (
    get_text,
    load_texts,
    get_schedule_image_path
)

__all__ = [
    'get_text',
    'load_texts',
    'get_schedule_image_path'
]
