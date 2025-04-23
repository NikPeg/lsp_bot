import sqlite3
import asyncio
from typing import Optional, List, Dict, Any

from database.models import User, get_connection, init_db
from config import DATABASE_PATH, DEFAULT_LANGUAGE

# Инициализируем базу данных при импорте модуля
init_db(DATABASE_PATH)

async def set_user_language(user_id: int, language: str) -> None:
    """
    Устанавливает или обновляет язык для пользователя

    Аргументы:
        user_id (int): Идентификатор пользователя
        language (str): Код языка (ru, en, ar)
    """
    try:
        await asyncio.to_thread(_set_user_language_sync, user_id, language)
    except Exception as e:
        print(f"Error setting user language: {e}")

def _set_user_language_sync(user_id: int, language: str) -> None:
    """
    Синхронная версия функции set_user_language
    """
    conn = get_connection(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users (user_id, language)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET 
        language = ?,
        last_activity = CURRENT_TIMESTAMP
        """,
        (user_id, language, language)
    )

    conn.commit()
    conn.close()

async def get_user_language(user_id: int) -> Optional[str]:
    """
    Получает язык пользователя

    Аргументы:
        user_id (int): Идентификатор пользователя

    Возвращает:
        Optional[str]: Код языка или None, если пользователь не найден
    """
    try:
        return await asyncio.to_thread(_get_user_language_sync, user_id)
    except Exception as e:
        print(f"Error getting user language: {e}")
        return DEFAULT_LANGUAGE

def _get_user_language_sync(user_id: int) -> Optional[str]:
    """
    Синхронная версия функции get_user_language
    """
    conn = get_connection(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT language FROM users WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None

async def set_user_faculty(user_id: int, faculty: Optional[str]) -> None:
    """
    Устанавливает или обновляет факультет для пользователя

    Аргументы:
        user_id (int): Идентификатор пользователя
        faculty (Optional[str]): Название факультета или None для сброса
    """
    try:
        await asyncio.to_thread(_set_user_faculty_sync, user_id, faculty)
    except Exception as e:
        print(f"Error setting user faculty: {e}")

def _set_user_faculty_sync(user_id: int, faculty: Optional[str]) -> None:
    """
    Синхронная версия функции set_user_faculty
    """
    conn = get_connection(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users (user_id, faculty, language)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET 
        faculty = ?,
        last_activity = CURRENT_TIMESTAMP
        """,
        (user_id, faculty, DEFAULT_LANGUAGE, faculty)
    )

    conn.commit()
    conn.close()

async def get_user_faculty(user_id: int) -> Optional[str]:
    """
    Получает факультет пользователя

    Аргументы:
        user_id (int): Идентификатор пользователя

    Возвращает:
        Optional[str]: Название факультета или None, если не выбран
    """
    try:
        return await asyncio.to_thread(_get_user_faculty_sync, user_id)
    except Exception as e:
        print(f"Error getting user faculty: {e}")
        return None

def _get_user_faculty_sync(user_id: int) -> Optional[str]:
    """
    Синхронная версия функции get_user_faculty
    """
    conn = get_connection(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT faculty FROM users WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None

async def get_user(user_id: int) -> Optional[User]:
    """
    Получает всю информацию о пользователе

    Аргументы:
        user_id (int): Идентификатор пользователя

    Возвращает:
        Optional[User]: Объект пользователя или None, если не найден
    """
    try:
        return await asyncio.to_thread(_get_user_sync, user_id)
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def _get_user_sync(user_id: int) -> Optional[User]:
    """
    Синхронная версия функции get_user
    """
    conn = get_connection(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id, language, faculty, created_at, last_activity FROM users WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()
    conn.close()

    if not result:
        return None

    return User(
        user_id=result[0],
        language=result[1],
        faculty=result[2],
        created_at=result[3],
        last_activity=result[4]
    )

async def update_user_activity(user_id: int) -> None:
    """
    Обновляет время последней активности пользователя

    Аргументы:
        user_id (int): Идентификатор пользователя
    """
    try:
        await asyncio.to_thread(_update_user_activity_sync, user_id)
    except Exception as e:
        print(f"Error updating user activity: {e}")

def _update_user_activity_sync(user_id: int) -> None:
    """
    Синхронная версия функции update_user_activity
    """
    conn = get_connection(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users 
        SET last_activity = CURRENT_TIMESTAMP
        WHERE user_id = ?
        """,
        (user_id,)
    )

    conn.commit()
    conn.close()
