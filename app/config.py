import os
from pathlib import Path
from pydantic import BaseSettings, Field, HttpUrl, validator
from typing import Optional

class Settings(BaseSettings):
    # Основные настройки бота
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    ADMIN_GROUP_ID: int = Field(..., env="ADMIN_GROUP_ID")
    CHANNEL_LINK: HttpUrl = Field(..., env="CHANNEL_LINK")
    MATERIALS_FOLDER: Path = Field(..., env="MATERIALS_FOLDER")
    LANGUAGE_DEFAULT: str = Field("ru", env="LANGUAGE_DEFAULT")

    # Валидация и преобразование значений
    @validator("MATERIALS_FOLDER", pre=True)
    def validate_materials_folder(cls, value):
        path = Path(value)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return path

    @validator("LANGUAGE_DEFAULT")
    def validate_default_language(cls, value):
        if value not in ["ru", "en", "ar"]:
            return "ru"
        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Инициализация настроек
try:
    config = Settings()
except Exception as e:
    raise RuntimeError(f"Failed to load configuration: {e}")

def get_config() -> Settings:
    """Возвращает конфигурацию приложения"""
    return config
