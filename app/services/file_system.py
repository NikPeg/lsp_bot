"""
Модуль для работы с файловой системой как источником правды.
Предоставляет методы для получения информации о структуре учебных материалов.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Union
import asyncio
import time
from datetime import datetime
from loguru import logger

from app.config import settings


class FileSystemService:
    """
    Сервис для работы с файловой системой.
    Предоставляет методы для доступа к учебным материалам.
    """

    def __init__(self):
        """Инициализация сервиса."""
        self.materials_path = settings.materials_path
        self.cache = {}  # Кэш для результатов сканирования
        self.cache_timeout = 300  # Время жизни кэша в секундах (5 минут)
        self.cache_timestamp = {}  # Время последнего обновления кэша

    async def get_faculties(self) -> List[str]:
        """
        Получает список доступных факультетов.

        Returns:
            List[str]: Список кодов факультетов.
        """
        cache_key = "faculties"

        # Проверяем кэш
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]

        faculties = []
        try:
            # Проверяем, что основная папка существует
            if not self.materials_path.exists():
                logger.warning(f"Папка с материалами не найдена: {self.materials_path}")
                return []

            # Получаем все подпапки в основной папке (факультеты)
            for item in self.materials_path.iterdir():
                if item.is_dir():
                    # Извлекаем код факультета из имени папки
                    faculty_code = item.name.split("_")[-1] if "_" in item.name else item.name
                    faculties.append(faculty_code)

            # Кэшируем результат
            self._update_cache(cache_key, faculties)

            return faculties

        except Exception as e:
            logger.error(f"Ошибка при получении списка факультетов: {e}")
            return []

    async def get_subjects(self, faculty: str) -> List[str]:
        """
        Получает список предметов для выбранного факультета.

        Args:
            faculty (str): Код факультета.

        Returns:
            List[str]: Список предметов.
        """
        cache_key = f"subjects_{faculty}"

        # Проверяем кэш
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]

        subjects = []
        try:
            faculty_path = self._get_faculty_path(faculty)

            if not faculty_path.exists():
                logger.warning(f"Папка факультета не найдена: {faculty_path}")
                return []

            # Получаем все подпапки в папке факультета (предметы)
            for item in faculty_path.iterdir():
                if item.is_dir():
                    subjects.append(item.name)

            # Кэшируем результат
            self._update_cache(cache_key, subjects)

            return subjects

        except Exception as e:
            logger.error(f"Ошибка при получении списка предметов для факультета {faculty}: {e}")
            return []

    async def get_material_types(self, faculty: str, subject: str) -> List[str]:
        """
        Получает список типов материалов для выбранного предмета.

        Args:
            faculty (str): Код факультета.
            subject (str): Название предмета.

        Returns:
            List[str]: Список типов материалов.
        """
        cache_key = f"material_types_{faculty}_{subject}"

        # Проверяем кэш
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]

        material_types = []
        try:
            subject_path = self._get_subject_path(faculty, subject)

            if not subject_path.exists():
                logger.warning(f"Папка предмета не найдена: {subject_path}")
                return []

            # Получаем все подпапки в папке предмета (типы материалов)
            for item in subject_path.iterdir():
                if item.is_dir():
                    material_types.append(item.name)

            # Кэшируем результат
            self._update_cache(cache_key, material_types)

            return material_types

        except Exception as e:
            logger.error(f"Ошибка при получении типов материалов для предмета {subject}: {e}")
            return []

    async def get_semesters(self, faculty: str, subject: str, material_type: str) -> List[str]:
        """
        Получает список семестров для выбранного типа материала.

        Args:
            faculty (str): Код факультета.
            subject (str): Название предмета.
            material_type (str): Тип материала.

        Returns:
            List[str]: Список семестров.
        """
        cache_key = f"semesters_{faculty}_{subject}_{material_type}"

        # Проверяем кэш
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]

        semesters = []
        try:
            material_type_path = self._get_material_type_path(faculty, subject, material_type)

            if not material_type_path.exists():
                logger.warning(f"Папка типа материала не найдена: {material_type_path}")
                return []

            # Получаем все подпапки в папке типа материала (семестры)
            for item in material_type_path.iterdir():
                if item.is_dir():
                    semesters.append(item.name)

            # Кэшируем результат
            self._update_cache(cache_key, semesters)

            return semesters

        except Exception as e:
            logger.error(f"Ошибка при получении семестров для типа материала {material_type}: {e}")
            return []

    async def get_materials(self, faculty: str, subject: str, material_type: str, semester: str) -> List[str]:
        """
        Получает список материалов для выбранного семестра.

        Args:
            faculty (str): Код факультета.
            subject (str): Название предмета.
            material_type (str): Тип материала.
            semester (str): Семестр.

        Returns:
            List[str]: Список материалов.
        """
        cache_key = f"materials_{faculty}_{subject}_{material_type}_{semester}"

        # Проверяем кэш (но с более коротким временем жизни)
        if self._is_cache_valid(cache_key, timeout=60):  # 1 минута для файлов
            return self.cache[cache_key]

        materials = []
        try:
            semester_path = self._get_semester_path(faculty, subject, material_type, semester)

            if not semester_path.exists():
                logger.warning(f"Папка семестра не найдена: {semester_path}")
                return []

            # Получаем все файлы в папке семестра
            for item in semester_path.iterdir():
                if item.is_file():
                    materials.append(item.name)

            # Кэшируем результат
            self._update_cache(cache_key, materials)

            return materials

        except Exception as e:
            logger.error(f"Ошибка при получении материалов для семестра {semester}: {e}")
            return []

    async def get_material_path(self, faculty: str, subject: str, material_type: str, semester: str, material: str) -> Path:
        """
        Получает путь к конкретному материалу.

        Args:
            faculty (str): Код факультета.
            subject (str): Название предмета.
            material_type (str): Тип материала.
            semester (str): Семестр.
            material (str): Название материала.

        Returns:
            Path: Путь к файлу материала.
        """
        try:
            semester_path = self._get_semester_path(faculty, subject, material_type, semester)
            material_path = semester_path / material

            if not material_path.exists():
                logger.warning(f"Файл материала не найден: {material_path}")
                return Path()

            return material_path

        except Exception as e:
            logger.error(f"Ошибка при получении пути к материалу {material}: {e}")
            return Path()

    async def clear_cache(self):
        """Очищает весь кэш."""
        self.cache = {}
        self.cache_timestamp = {}
        logger.info("Кэш файловой системы очищен")

    def _get_faculty_path(self, faculty: str) -> Path:
        """
        Получает путь к папке факультета.

        Args:
            faculty (str): Код факультета.

        Returns:
            Path: Путь к папке факультета.
        """
        # Для обратной совместимости проверяем разные форматы имени папки
        faculty_path = self.materials_path / f"faculty_{faculty}"

        if not faculty_path.exists():
            # Пробуем другие варианты имени
            for item in self.materials_path.iterdir():
                if item.is_dir() and item.name.endswith(faculty):
                    return item

        return faculty_path

    def _get_subject_path(self, faculty: str, subject: str) -> Path:
        """
        Получает путь к папке предмета.

        Args:
            faculty (str): Код факультета.
            subject (str): Название предмета.

        Returns:
            Path: Путь к папке предмета.
        """
        faculty_path = self._get_faculty_path(faculty)
        return faculty_path / subject

    def _get_material_type_path(self, faculty: str, subject: str, material_type: str) -> Path:
        """
        Получает путь к папке типа материала.

        Args:
            faculty (str): Код факультета.
            subject (str): Название предмета.
            material_type (str): Тип материала.

        Returns:
            Path: Путь к папке типа материала.
        """
        subject_path = self._get_subject_path(faculty, subject)
        return subject_path / material_type

    def _get_semester_path(self, faculty: str, subject: str, material_type: str, semester: str) -> Path:
        """
        Получает путь к папке семестра.

        Args:
            faculty (str): Код факультета.
            subject (str): Название предмета.
            material_type (str): Тип материала.
            semester (str): Семестр.

        Returns:
            Path: Путь к папке семестра.
        """
        material_type_path = self._get_material_type_path(faculty, subject, material_type)
        return material_type_path / semester

    def _is_cache_valid(self, key: str, timeout: int = None) -> bool:
        """
        Проверяет, действителен ли кэш для указанного ключа.

        Args:
            key (str): Ключ кэша.
            timeout (int, optional): Время жизни кэша в секундах.

        Returns:
            bool: True, если кэш действителен, иначе False.
        """
        if timeout is None:
            timeout = self.cache_timeout

        if key not in self.cache or key not in self.cache_timestamp:
            return False

        current_time = time.time()
        cache_time = self.cache_timestamp.get(key, 0)

        return current_time - cache_time < timeout

    def _update_cache(self, key: str, value):
        """
        Обновляет кэш для указанного ключа.

        Args:
            key (str): Ключ кэша.
            value: Значение для сохранения в кэше.
        """
        self.cache[key] = value
        self.cache_timestamp[key] = time.time()
