import sqlite3
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    """
    Модель пользователя для хранения в базе данных

    Атрибуты:
        user_id (int): Идентификатор пользователя в Telegram
        language (str): Код выбранного языка (ru, en, ar)
        faculty (Optional[str]): Выбранный факультет или None если не выбран
        created_at (str): Дата и время создания записи
        last_activity (str): Дата и время последней активности
    """
    user_id: int
    language: str
    faculty: Optional[str] = None
    created_at: str = None
    last_activity: str = None

def init_db(db_path: str) -> None:
    """
    Инициализирует базу данных и создает необходимые таблицы

    Аргументы:
        db_path (str): Путь к файлу базы данных
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаем таблицу пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        language TEXT NOT NULL,
        faculty TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

def get_connection(db_path: str) -> sqlite3.Connection:
    """
    Получает соединение с базой данных

    Аргументы:
        db_path (str): Путь к файлу базы данных

    Возвращает:
        sqlite3.Connection: Объект соединения с базой данных
    """
    return sqlite3.connect(db_path)
