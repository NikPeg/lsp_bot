from pathlib import Path
from .file_manager import FileManager
from .menu_builder import MenuBuilder
from .user_activity import UserActivityTracker

# Инициализация сервисов
data_path = Path("data/users/activity.json")
file_manager = FileManager()
menu_builder = MenuBuilder(file_manager)
user_activity = UserActivityTracker(data_path)

__all__ = [
    'FileManager',
    'MenuBuilder',
    'UserActivityTracker',
    'file_manager',
    'menu_builder',
    'user_activity'
]
