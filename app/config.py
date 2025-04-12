"""
Модуль для загрузки и работы с конфигурацией из .env файла.
Использует pydantic для валидации и установки значений по умолчанию.
"""

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Загрузка переменных из .env файла
load_dotenv()

# Базовая директория проекта
BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из переменных окружения."""

    # Telegram Bot Token (обязательный параметр)
    BOT_TOKEN: str

    # ID группы администраторов (обязательный параметр, будет преобразован в int)
    ADMIN_GROUP_ID: int

    # Ссылка на канал
    CHANNEL_LINK: str = "https://t.me/your_channel"

    # Папка с материалами (relative to BASE_DIR)
    MATERIALS_FOLDER: str = "data/materials"

    # Папка с изображениями расписаний
    SCHEDULE_IMAGES_FOLDER: str = "data/images/schedule"

    # Папка для хранения данных пользователей
    USERS_DATA_FOLDER: str = "data/users"

    # Папка с текстами интерфейса на разных языках
    TEXTS_FOLDER: str = "data/texts"

    # Настройки языка
    LANGUAGE_DEFAULT: str = "ru"
    AVAILABLE_LANGUAGES: List[str] = ["ru", "en", "ar"]

    # Имена факультетов (можно изменить при необходимости)
    FACULTY_L_NAME: str = "Лечебный факультет"
    FACULTY_S_NAME: str = "Стоматологический факультет"
    FACULTY_P_NAME: str = "Педиатрический факультет"

    class Config:
        """Настройки pydantic."""
        env_file = ".env"
        case_sensitive = True

    @property
    def materials_path(self) -> Path:
        """Возвращает полный путь к папке с материалами."""
        return BASE_DIR / self.MATERIALS_FOLDER

    @property
    def schedule_images_path(self) -> Path:
        """Возвращает полный путь к папке с изображениями расписаний."""
        return BASE_DIR / self.SCHEDULE_IMAGES_FOLDER

    @property
    def users_data_path(self) -> Path:
        """Возвращает полный путь к папке с данными пользователей."""
        return BASE_DIR / self.USERS_DATA_FOLDER

    @property
    def texts_path(self) -> Path:
        """Возвращает полный путь к папке с текстами."""
        return BASE_DIR / self.TEXTS_FOLDER

    def ensure_folders_exist(self):
        """Создаёт необходимые папки, если они не существуют."""
        for path in [
            self.materials_path,
            self.schedule_images_path,
            self.users_data_path,
            self.texts_path
        ]:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                print(f"Создана папка: {path}")


# Экземпляр настроек для использования в приложении
settings = Settings()

# Создание необходимых папок при импорте конфигурации
settings.ensure_folders_exist()
