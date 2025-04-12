"""
Модуль для создания динамических клавиатур на основе файловой структуры.
Включает функции для генерации клавиатур с предметами, материалами, семестрами и т.д.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger

from app.config import get_config
from app.utils.helpers import get_text

config = get_config()

def get_subjects_keyboard(subjects: list, language: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора предмета.

    Args:
        subjects (list): Список доступных предметов.
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура с предметами.
    """
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


def get_material_types_keyboard(material_types: list, language: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора типа материала.

    Args:
        material_types (list): Список доступных типов материалов.
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура с типами материалов.
    """
    keyboard = []

    # Словарь для локализованных названий типов материалов
    material_type_names = {
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

    # Добавляем кнопки для каждого типа материала
    for material_type in material_types:
        # Получаем локализованное название или используем оригинальное имя папки
        button_text = material_type_names.get(material_type, {}).get(language, material_type)

        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
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


def get_semesters_keyboard(material_type: str, semesters: list, language: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора семестра.

    Args:
        material_type (str): Тип материала.
        semesters (list): Список доступных семестров.
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура с семестрами.
    """
    keyboard = []

    # Словарь для локализованных названий семестров
    semester_names = {
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
        "semester3": {
            "ru": "3 семестр",
            "en": "3rd semester",
            "ar": "الفصل الدراسي الثالث"
        },
        "semester4": {
            "ru": "4 семестр",
            "en": "4th semester",
            "ar": "الفصل الدراسي الرابع"
        },
        "semester5": {
            "ru": "5 семестр",
            "en": "5th semester",
            "ar": "الفصل الدراسي الخامس"
        },
        "semester6": {
            "ru": "6 семестр",
            "en": "6th semester",
            "ar": "الفصل الدراسي السادس"
        },
        "semester7": {
            "ru": "7 семестр",
            "en": "7th semester",
            "ar": "الفصل الدراسي السابع"
        },
        "semester8": {
            "ru": "8 семестр",
            "en": "8th semester",
            "ar": "الفصل الدراسي الثامن"
        },
        "semester9": {
            "ru": "9 семестр",
            "en": "9th semester",
            "ar": "الفصل الدراسي التاسع"
        },
        "semester10": {
            "ru": "10 семестр",
            "en": "10th semester",
            "ar": "الفصل الدراسي العاشر"
        },
        "semester11": {
            "ru": "11 семестр",
            "en": "11th semester",
            "ar": "الفصل الدراسي الحادي عشر"
        },
        "semester12": {
            "ru": "12 семестр",
            "en": "12th semester",
            "ar": "الفصل الدراسي الثاني عشر"
        }
    }

    # Сортируем семестры по номеру, если это возможно
    try:
        sorted_semesters = sorted(semesters, key=lambda x: int(x.replace("semester", "")))
    except (ValueError, AttributeError):
        sorted_semesters = semesters

    # Группируем кнопки по две в строке
    for i in range(0, len(sorted_semesters), 2):
        row = []

        # Добавляем первую кнопку в строку
        semester = sorted_semesters[i]
        button_text = semester_names.get(semester, {}).get(language, semester)
        row.append(
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"semester_{material_type}_{semester}"
            )
        )

        # Добавляем вторую кнопку, если она есть
        if i + 1 < len(sorted_semesters):
            semester = sorted_semesters[i + 1]
            button_text = semester_names.get(semester, {}).get(language, semester)
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


def get_materials_keyboard(material_type: str, semester: str, materials: list, language: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора конкретного материала.

    Args:
        material_type (str): Тип материала.
        semester (str): Выбранный семестр.
        materials (list): Список доступных материалов.
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура с материалами.
    """
    keyboard = []

    # Добавляем кнопки для каждого материала
    for material in materials:
        # Обрезаем длинные названия файлов для кнопок
        button_text = material
        if len(button_text) > 30:
            button_text = button_text[:27] + "..."

        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"file_{material_type}_{semester}_{material}"
            )
        ])

    # Добавляем кнопку возврата
    keyboard.append([
        InlineKeyboardButton(
            text=get_text(language, "back_button"),
            callback_data="back_to_semesters"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_faculty_keyboard_dynamic(faculties: list, language: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора факультета на основе доступных факультетов.

    Args:
        faculties (list): Список доступных факультетов.
        language (str): Код языка пользователя.

    Returns:
        InlineKeyboardMarkup: Клавиатура с факультетами.
    """
    keyboard = []

    # Словарь для локализованных названий факультетов
    faculty_names = {
        "L": {
            "ru": config.FACULTY_L_NAME,
            "en": "Faculty of Medicine",
            "ar": "كلية الطب"
        },
        "S": {
            "ru": config.FACULTY_S_NAME,
            "en": "Faculty of Dentistry",
            "ar": "كلية طب الأسنان"
        },
        "P": {
            "ru": config.FACULTY_P_NAME,
            "en": "Faculty of Pediatrics",
            "ar": "كلية طب الأطفال"
        }
    }

    # Добавляем кнопки для каждого факультета
    for faculty in faculties:
        button_text = faculty_names.get(faculty, {}).get(language, faculty)
        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"faculty_{faculty}"
            )
        ])

    # Добавляем кнопку возврата в основное меню
    keyboard.append([
        InlineKeyboardButton(
            text=get_text(language, "back_to_main_menu"),
            callback_data="main_menu"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
