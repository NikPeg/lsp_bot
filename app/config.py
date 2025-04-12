import os
from pathlib import Path
from typing import Optional

from pydantic import Field, HttpUrl, validator
from pydantic_settings import BaseSettings
from loguru import logger

class Settings(BaseSettings):
    # Основные настройки бота
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    ADMIN_GROUP_ID: int = Field(..., env="ADMIN_GROUP_ID")
    CHANNEL_LINK: HttpUrl = Field(..., env="CHANNEL_LINK")
    MATERIALS_FOLDER: Path = Field(..., env="MATERIALS_FOLDER")
    LANGUAGE_DEFAULT: str = Field("ru", env="LANGUAGE_DEFAULT")
    IMAGES_FOLDER: str = Field(..., env="IMAGES_FOLDER")

    # Валидация и преобразование значений
    @validator("MATERIALS_FOLDER", pre=True)
    def validate_materials_folder(cls, value):
        path = Path(value)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created materials folder: {path}")
        return path

    @validator("LANGUAGE_DEFAULT")
    def validate_default_language(cls, value):
        if value not in ["ru", "en", "ar"]:
            logger.warning(f"Invalid default language: {value}, using 'ru'")
            return "ru"
        return value

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

def get_config() -> Settings:
    """Возвращает конфигурацию приложения"""
    try:
        config = Settings()
        logger.info("Configuration loaded successfully")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise RuntimeError(f"Configuration error: {e}")
