from typing import Dict

# Словарь эмодзи для различных кнопок и категорий
EMOJI_DICT = {
    # Главное меню
    "profile_button": "👤",
    "learning_center_button": "📚",
    "schedule_button": "📆",
    "channel_button": "📢",

    # Навигация и действия
    "back_button": "🔙",
    "back_to_main_menu": "🏠",
    "faculty_button": "🏫",
    "language_settings_button": "🌐",

    # Типы материалов
    "folder": "📁",
    "file": "📄",
    "pdf_file": "📑",
    "image_file": "🖼️",
    "document_file": "📃",
    "audio_file": "🎵",
    "video_file": "🎬",

    # Расписание
    "deanery_button": "🏢",
    "sports_doctor_button": "⚕️",
    "libraries_button": "📚",
    "pass_making_button": "🪪",
    "practice_button": "👨‍⚕️",

    # Факультеты
    "faculty_L_name": "🏥",  # Лечебный
    "faculty_S_name": "🦷",  # Стоматологический
    "faculty_P_name": "👶",  # Педиатрический

    # Статусы
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",

    # Прочее
    "loading": "⏳",
    "search": "🔍",
    "settings": "⚙️"
}

def add_emoji_to_text(emoji: str, text: str) -> str:
    """
    Добавляет эмодзи в начало текста

    Аргументы:
        emoji (str): Эмодзи для добавления
        text (str): Исходный текст

    Возвращает:
        str: Текст с добавленным эмодзи
    """
    return f"{emoji} {text}"

def get_emoji_for_key(key: str, default: str = "") -> str:
    """
    Получает эмодзи для заданного ключа

    Аргументы:
        key (str): Ключ для поиска эмодзи
        default (str): Эмодзи по умолчанию, если ключ не найден

    Возвращает:
        str: Эмодзи для ключа или значение по умолчанию
    """
    return EMOJI_DICT.get(key, default)

def get_emoji_for_file(filename: str) -> str:
    """
    Получает эмодзи для файла на основе его расширения

    Аргументы:
        filename (str): Имя файла

    Возвращает:
        str: Эмодзи, соответствующее типу файла
    """
    ext = filename.split('.')[-1].lower() if '.' in filename else ""

    if ext in ["pdf"]:
        return get_emoji_for_key("pdf_file")
    elif ext in ["jpg", "jpeg", "png", "gif", "bmp"]:
        return get_emoji_for_key("image_file")
    elif ext in ["doc", "docx", "txt", "rtf"]:
        return get_emoji_for_key("document_file")
    elif ext in ["mp3", "wav", "ogg"]:
        return get_emoji_for_key("audio_file")
    elif ext in ["mp4", "avi", "mov", "mkv"]:
        return get_emoji_for_key("video_file")
    else:
        return get_emoji_for_key("file")
