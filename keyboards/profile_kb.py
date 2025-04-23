from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.text_manager import get_text
from services.file_manager import get_faculties
from utils.emoji import add_emoji_to_text

async def get_faculty_selection_keyboard(language: str) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для выбора факультета

    Аргументы:
        language (str): Код языка (ru, en, ar)

    Возвращает:
        InlineKeyboardMarkup: Клавиатура с кнопками факультетов
    """
    keyboard = InlineKeyboardMarkup(row_width=1)

    # Получаем список факультетов из файловой системы
    faculties = await get_faculties()

    # Добавляем кнопку для каждого факультета
    for faculty in faculties:
        # Пытаемся найти перевод названия факультета
        faculty_key = f"faculty_{faculty.split()[0][0]}_name"  # Например, "faculty_L_name" для "Лечебный факультет"
        faculty_text = get_text(language, faculty_key, default=faculty)
        faculty_text = add_emoji_to_text("🏫", faculty_text)

        keyboard.add(InlineKeyboardButton(
            text=faculty_text,
            callback_data=f"faculty:{faculty}"
        ))

    # Добавляем кнопку для выбора языка
    language_settings_text = add_emoji_to_text("🌐", get_text(language, "language_settings_button"))
    keyboard.add(InlineKeyboardButton(
        text=language_settings_text,
        callback_data="open_language_settings"
    ))

    # Добавляем кнопку для возврата в главное меню
    back_text = add_emoji_to_text("🔙", get_text(language, "back_to_main_menu"))
    keyboard.add(InlineKeyboardButton(
        text=back_text,
        callback_data="back_to_main"
    ))

    return keyboard

def get_language_settings_keyboard(language: str) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для настроек языка

    Аргументы:
        language (str): Текущий код языка (ru, en, ar)

    Возвращает:
        InlineKeyboardMarkup: Клавиатура с кнопками языков
    """
    keyboard = InlineKeyboardMarkup(row_width=1)

    # Добавляем кнопки для выбора языка
    keyboard.add(
        InlineKeyboardButton(
            text="🇬🇧 English" + (" ✓" if language == "en" else ""),
            callback_data="change_language:en"
        ),
        InlineKeyboardButton(
            text="🇷🇺 Русский" + (" ✓" if language == "ru" else ""),
            callback_data="change_language:ru"
        ),
        InlineKeyboardButton(
            text="🇸🇦 العربية" + (" ✓" if language == "ar" else ""),
            callback_data="change_language:ar"
        )
    )

    # Добавляем кнопку назад
    back_text = add_emoji_to_text("🔙", get_text(language, "back_button"))
    keyboard.add(InlineKeyboardButton(
        text=back_text,
        callback_data="back_to_profile"
    ))

    return keyboard
