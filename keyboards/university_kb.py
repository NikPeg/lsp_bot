from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.text_manager import get_text
from services.file_manager import get_faculties
from utils.emoji import add_emoji_to_text

# Короткие имена для университетов (для callback_data и локализации)
UNIVERSITY_SHORTCUTS = [
    "spbgpmu",  # Санкт-Петербургский государственный педиатрический медицинский университет
    "vmeda",    # Военно-медицинская академия имени С. М. Кирова
    "szgmu",    # Северо-Западный государственный медицинский университет им. И.И.Мечникова
    "reaviz",   # УНИВЕРСИТЕТ РЕАВИЗ
    "spbmsi"    # Санкт-Петербургский медико-социальный институт
]

async def get_university_selection_keyboard(language: str, selected_university: str = None) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для выбора университета

    Аргументы:
        language (str): Код языка (ru, en, ar)
        selected_university (str, optional): Короткое имя выбранного университета

    Возвращает:
        InlineKeyboardMarkup: Клавиатура с кнопками университетов
    """
    builder = InlineKeyboardBuilder()

    for univ_shortcut in UNIVERSITY_SHORTCUTS:
        # Получаем переведенное название университета
        univ_text = get_text(language, f"univ_{univ_shortcut}")

        # Добавляем галочку для выбранного университета
        if univ_shortcut == selected_university:
            univ_text = add_emoji_to_text("🏛️", univ_text) + " ✅"
        else:
            univ_text = add_emoji_to_text("🏛️", univ_text)

        builder.row(
            InlineKeyboardButton(text=univ_text, callback_data=f"univ:{univ_shortcut}")
        )

    # Добавляем кнопку для выбора языка
    language_settings_text = add_emoji_to_text("🌐", get_text(language, "language_settings_button"))
    builder.row(
        InlineKeyboardButton(text=language_settings_text, callback_data="open_language_settings")
    )

    # Добавляем кнопку для возврата в главное меню
    back_text = add_emoji_to_text("🔙", get_text(language, "back_to_main_menu"))
    builder.row(
        InlineKeyboardButton(text=back_text, callback_data="back_to_main")
    )

    return builder.as_markup()

async def get_faculty_selection_keyboard_with_selected(language: str, selected_university: str = None, selected_faculty: str = None) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для выбора факультета с отметкой выбранного

    Аргументы:
        language (str): Код языка (ru, en, ar)
        selected_university (str, optional): Короткое имя выбранного университета
        selected_faculty (str, optional): Выбранный факультет

    Возвращает:
        InlineKeyboardMarkup: Клавиатура с кнопками факультетов
    """
    builder = InlineKeyboardBuilder()

    # Добавляем информацию о выбранном университете
    if selected_university:
        # Получаем переведенное название университета
        university_text = get_text(language, f"univ_{selected_university}")

        university_text = add_emoji_to_text("🏛️", university_text) + " ✅"
        builder.row(
            InlineKeyboardButton(text=university_text, callback_data=f"back_to_univ")
        )

    # Получаем список факультетов из файловой системы
    faculties = await get_faculties()

    # Добавляем кнопку для каждого факультета
    for faculty in faculties:
        # Пытаемся найти перевод названия факультета
        faculty_key = f"faculty_{faculty.split()[0][0]}_name"  # Например, "faculty_L_name" для "Лечебный факультет"
        faculty_text = get_text(language, faculty_key, default=faculty)

        # Добавляем галочку, если это выбранный факультет
        if faculty == selected_faculty:
            faculty_text = add_emoji_to_text("🏫", faculty_text) + " ✅"
        else:
            faculty_text = add_emoji_to_text("🏫", faculty_text)

        builder.row(
            InlineKeyboardButton(text=faculty_text, callback_data=f"faculty:{faculty}")
        )

    # Добавляем кнопку для выбора языка
    language_settings_text = add_emoji_to_text("🌐", get_text(language, "language_settings_button"))
    builder.row(
        InlineKeyboardButton(text=language_settings_text, callback_data="open_language_settings")
    )

    # Добавляем кнопку для возврата в главное меню
    back_text = add_emoji_to_text("🔙", get_text(language, "back_to_main_menu"))
    builder.row(
        InlineKeyboardButton(text=back_text, callback_data="back_to_main")
    )

    return builder.as_markup()
