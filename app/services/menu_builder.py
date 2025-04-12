"""
Модуль для динамического построения меню на основе файловой структуры.
Преобразует структуру папок с материалами в элементы меню для бота.
"""

from typing import List, Dict, Optional, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger

from app.config import settings
from app.services.file_system import FileSystemService
from app.utils.helpers import get_text


class MenuBuilderService:
    """
    Сервис для построения меню на основе файловой структуры.
    Преобразует папки и файлы в элементы меню бота.
    """

    def __init__(self):
        """Инициализация сервиса."""
        self.file_system_service = FileSystemService()

        # Словари для перевода технических названий
        self.faculty_names = {
            "L": {
                "ru": settings.FACULTY_L_NAME,
                "en": "Faculty of Medicine",
                "ar": "كلية الطب"
            },
            "S": {
                "ru": settings.FACULTY_S_NAME,
                "en": "Faculty of Dentistry",
                "ar": "كلية طب الأسنان"
            },
            "P": {
                "ru": settings.FACULTY_P_NAME,
                "en": "Faculty of Pediatrics",
                "ar": "كلية طب الأطفال"
            }
        }

        self.material_types = {
            "lectures": {
                "ru": "Лекции",
                "en": "Lectures",
                "ar": "المحاضرات"
            },
            "books": {
                "ru": "Книги",
                "en": "Books",
                "ar": "الكتب"
            },
            "atlases": {
                "ru": "Атласы",
                "en": "Atlases",
                "ar": "الأطالس"
            },
            "methods": {
                "ru": "Методички",
                "en": "Methodological materials",
                "ar": "المواد المنهجية"
            },
            "exams": {
                "ru": "Экзаменационные материалы",
                "en": "Exam materials",
                "ar": "مواد الامتحان"
            },
            "notes": {
                "ru": "Шпаргалки и конспекты",
                "en": "Notes and summaries",
                "ar": "الملاحظات والملخصات"
            }
        }

        self.semester_names = {
            "semester1": {
                "ru": "1 семестр",
                "en": "1st semester",
                "ar": "الفصل الدراسي الأول"
            },
            "semester2": {
                "ru": "2 семестр",
                "en": "2nd semester",
                "ar": "الفصل الدراسي الثاني"
            },
            # ... добавьте остальные семестры по аналогии
        }

    async def build_faculty_menu(self, language: str) -> InlineKeyboardMarkup:
        """
        Строит меню выбора факультета на основе доступных папок.

        Args:
            language (str): Код языка пользователя.

        Returns:
            InlineKeyboardMarkup: Клавиатура с факультетами.
        """
        faculties = await self.file_system_service.get_faculties()
        keyboard = []

        for faculty in faculties:
            # Получаем локализованное название
            faculty_name = self.faculty_names.get(faculty, {}).get(language, faculty)

            keyboard.append([
                InlineKeyboardButton(
                    text=faculty_name,
                    callback_data=f"faculty_{faculty}"
                )
            ])

        # Добавляем кнопку возврата
        keyboard.append([
            InlineKeyboardButton(
                text=get_text(language, "back_to_main_menu"),
                callback_data="main_menu"
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    async def build_subjects_menu(self, faculty: str, language: str) -> InlineKeyboardMarkup:
        """
        Строит меню выбора предмета на основе доступных папок.

        Args:
            faculty (str): Код факультета.
            language (str): Код языка пользователя.

        Returns:
            InlineKeyboardMarkup: Клавиатура с предметами.
        """
        subjects = await self.file_system_service.get_subjects(faculty)
        keyboard = []

        # Группируем кнопки по две в строке
        for i in range(0, len(subjects), 2):
            row = []
            # Добавляем первую кнопку в строку
            subject = subjects[i]
            row.append(
                InlineKeyboardButton(
                    text=subject,
                    callback_data=f"subject_{subject}"
                )
            )

            # Добавляем вторую кнопку, если она есть
            if i + 1 < len(subjects):
                subject = subjects[i + 1]
                row.append(
                    InlineKeyboardButton(
                        text=subject,
                        callback_data=f"subject_{subject}"
                    )
                )

            keyboard.append(row)

        # Добавляем кнопку возврата
        keyboard.append([
            InlineKeyboardButton(
                text=get_text(language, "back_button"),
                callback_data="learning_center"
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    async def build_material_types_menu(self, faculty: str, subject: str, language: str) -> InlineKeyboardMarkup:
        """
        Строит меню выбора типа материала на основе доступных папок.

        Args:
            faculty (str): Код факультета.
            subject (str): Название предмета.
            language (str): Код языка пользователя.

        Returns:
            InlineKeyboardMarkup: Клавиатура с типами материалов.
        """
        material_types = await self.file_system_service.get_material_types(faculty, subject)
        keyboard = []

        for material_type in material_types:
            # Получаем локализованное название
            type_name = self.material_types.get(material_type, {}).get(language, material_type)

            keyboard.append([
                InlineKeyboardButton(
                    text=type_name,
                    callback_data=f"material_type_{material_type}"
                )
            ])

        # Добавляем кнопку возврата
        keyboard.append([
            InlineKeyboardButton(
                text=get_text(language, "back_button"),
                callback_data="back_to_subjects"
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    async def build_semesters_menu(self, faculty: str, subject: str, material_type: str, language: str) -> InlineKeyboardMarkup:
        """
        Строит меню выбора семестра на основе доступных папок.

        Args:
            faculty (str): Код факультета.
            subject (str): Название предмета.
            material_type (str): Тип материала.
            language (str): Код языка пользователя.

        Returns:
            InlineKeyboardMarkup: Клавиатура с семестрами.
        """
        semesters = await self.file_system_service.get_semesters(faculty, subject, material_type)
        keyboard = []

        # Сортируем семестры по номеру
        try:
            sorted_semesters = sorted(semesters, key=lambda x: int(x.replace("semester", "")))
        except (ValueError, AttributeError):
            sorted_semesters = semesters

        # Группируем кнопки по две в строке
        for i in range(0, len(sorted_semesters), 2):
            row = []

            # Добавляем первую кнопку в строку
            semester = sorted_semesters[i]
            button_text = self.semester_names.get(semester, {}).get(language, semester)
            row.append(
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"semester_{material_type}_{semester}"
                )
            )

            # Добавляем вторую кнопку, если она есть
            if i + 1 < len(sorted_semesters):
                semester = sorted_semesters[i + 1]
                button_text = self.semester_names.get(semester, {}).get(language, semester)
                row.append(
                    InlineKeyboardButton(
                        text=button_text,
                        callback_data=f"semester_{material_type}_{semester}"
                    )
                )

            keyboard.append(row)

        # Добавляем кнопку возврата
        keyboard.append([
            InlineKeyboardButton(
                text=get_text(language, "back_button"),
                callback_data="back_to_material_types"
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    async def build_materials_menu(self, faculty: str, subject: str, material_type: str, semester: str, language: str) -> InlineKeyboardMarkup:
        """
        Строит меню выбора материала на основе доступных файлов.

        Args:
            faculty (str): Код факультета.
            subject (str): Название предмета.
            material_type (str): Тип материала.
            semester (str): Семестр.
            language (str): Код языка пользователя.

        Returns:
            InlineKeyboardMarkup: Клавиатура с материалами.
        """
        materials = await self.file_system_service.get_m
