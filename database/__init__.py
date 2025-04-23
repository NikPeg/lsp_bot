from database.models import User, init_db, get_connection
from database.db_manager import (
    set_user_language,
    get_user_language,
    set_user_faculty,
    get_user_faculty,
    get_user,
    update_user_activity
)

# Экспортируем основные функции для работы с БД
__all__ = [
    'User',
    'init_db',
    'set_user_language',
    'get_user_language',
    'set_user_faculty',
    'get_user_faculty',
    'get_user',
    'update_user_activity'
]