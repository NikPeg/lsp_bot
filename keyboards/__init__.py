from keyboards.language_kb import get_language_keyboard
from keyboards.main_kb import get_main_keyboard
from keyboards.profile_kb import get_faculty_selection_keyboard, get_language_settings_keyboard
from keyboards.learning_kb import get_navigation_keyboard
from keyboards.schedule_kb import get_schedule_keyboard
from keyboards.inline_kb import get_back_keyboard, get_channel_keyboard, get_after_file_keyboard
from keyboards.learning_kb import get_navigation_keyboard, get_path_by_id, get_path_id
from keyboards.university_kb import get_university_selection_keyboard, get_faculty_selection_keyboard_with_selected

__all__ = [
    'get_language_keyboard',
    'get_main_keyboard',
    'get_faculty_selection_keyboard',
    'get_language_settings_keyboard',
    'get_navigation_keyboard',
    'get_schedule_keyboard',
    'get_back_keyboard',
    'get_channel_keyboard',
    'get_after_file_keyboard',
    'get_path_by_id',
    'get_path_id',
    'get_university_selection_keyboard',
    'get_faculty_selection_keyboard_with_selected'
]
