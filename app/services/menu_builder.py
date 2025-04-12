from pathlib import Path
from typing import Dict, List, Optional, Tuple
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger

from app.services.file_manager import FileManager


class MenuBuilder:
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        self.cache = {}  # Кэш для хранения уже построенных меню

    async def build_faculty_menu(self) -> InlineKeyboardMarkup:
        """Строит меню выбора факультета"""
        cache_key = "faculty_menu"
        if cache_key in self.cache:
            return self.cache[cache_key]

        keyboard = InlineKeyboardMarkup(row_width=2)
        faculties = await self.file_manager.get_faculties()

        for faculty in faculties:
            keyboard.insert(
                InlineKeyboardButton(
                    text=faculty.name,
                    callback_data=f"faculty:{faculty.id}"
                )
            )

        self.cache[cache_key] = keyboard
        return keyboard

    async def build_subjects_menu(self, faculty_id: str) -> InlineKeyboardMarkup:
        """Строит меню выбора предмета для указанного факультета"""
        cache_key = f"subjects_menu:{faculty_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        keyboard = InlineKeyboardMarkup(row_width=2)
        subjects = await self.file_manager.get_subjects(faculty_id)

        for subject in subjects:
            keyboard.insert(
                InlineKeyboardButton(
                    text=subject.name,
                    callback_data=f"subject:{faculty_id}:{subject.id}"
                )
            )

        keyboard.row(
            InlineKeyboardButton(
                text="← Назад",
                callback_data="back_to_faculties"
            )
        )

        self.cache[cache_key] = keyboard
        return keyboard

    async def build_materials_menu(
            self,
            faculty_id: str,
            subject_id: str
    ) -> InlineKeyboardMarkup:
        """Строит меню выбора типа материалов"""
        cache_key = f"materials_menu:{faculty_id}:{subject_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        keyboard = InlineKeyboardMarkup(row_width=2)
        material_types = [
            ("Лекции", "lectures"),
            ("Книги", "books"),
            ("Атласы", "atlases"),
            ("Методички", "methods"),
            ("Экзамены", "exams"),
            ("Шпаргалки", "notes")
        ]

        for name, callback in material_types:
            keyboard.insert(
                InlineKeyboardButton(
                    text=name,
                    callback_data=f"material_type:{faculty_id}:{subject_id}:{callback}"
                )
            )

        keyboard.row(
            InlineKeyboardButton(
                text="← Назад",
                callback_data=f"back_to_subjects:{faculty_id}"
            )
        )

        self.cache[cache_key] = keyboard
        return keyboard

    async def build_semesters_menu(
            self,
            faculty_id: str,
            subject_id: str,
            material_type: str
    ) -> InlineKeyboardMarkup:
        """Строит меню выбора семестра"""
        cache_key = f"semesters_menu:{faculty_id}:{subject_id}:{material_type}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        keyboard = InlineKeyboardMarkup(row_width=2)
        semesters = await self.file_manager.get_semesters(
            faculty_id, subject_id, material_type
        )

        for semester in semesters:
            keyboard.insert(
                InlineKeyboardButton(
                    text=f"Семестр {semester}",
                    callback_data=f"semester:{faculty_id}:{subject_id}:{material_type}:{semester}"
                )
            )

        keyboard.row(
            InlineKeyboardButton(
                text="← Назад",
                callback_data=f"back_to_materials:{faculty_id}:{subject_id}"
            )
        )

        self.cache[cache_key] = keyboard
        return keyboard

    async def build_files_menu(
            self,
            faculty_id: str,
            subject_id: str,
            material_type: str,
            semester: str
    ) -> InlineKeyboardMarkup:
        """Строит меню выбора файлов"""
        cache_key = f"files_menu:{faculty_id}:{subject_id}:{material_type}:{semester}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        keyboard = InlineKeyboardMarkup(row_width=1)
        files = await self.file_manager.get_files(
            faculty_id, subject_id, material_type, semester
        )

        for file in files:
            keyboard.insert(
                InlineKeyboardButton(
                    text=file.name,
                    callback_data=f"file:{faculty_id}:{subject_id}:{material_type}:{semester}:{file.id}"
                )
            )

        keyboard.row(
            InlineKeyboardButton(
                text="← Назад",
                callback_data=f"back_to_semesters:{faculty_id}:{subject_id}:{material_type}"
            )
        )

        self.cache[cache_key] = keyboard
        return keyboard

    async def clear_cache(self, key: Optional[str] = None) -> None:
        """Очищает кэш меню"""
        if key:
            if key in self.cache:
                del self.cache[key]
        else:
            self.cache.clear()
        logger.info(f"Menu cache cleared {'for key: ' + key if key else 'completely'}")
