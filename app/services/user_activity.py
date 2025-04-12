import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from loguru import logger

class UserActivityTracker:
    def __init__(self, data_path: Path = Path("data/users/activity.json")):
        self.data_path = data_path
        self._ensure_data_dir_exists()
        self.data = self._load_data()

    def _ensure_data_dir_exists(self) -> None:
        """Создает директорию для хранения данных, если она не существует"""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_data(self) -> Dict[str, dict]:
        """Загружает данные о пользователях из файла"""
        try:
            if self.data_path.exists():
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading user activity data: {e}")
            return {}

    def _save_data(self) -> None:
        """Сохраняет данные о пользователях в файл"""
        try:
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving user activity data: {e}")

    def register_user(self, user_id: int) -> None:
        """Регистрирует нового пользователя"""
        user_id_str = str(user_id)
        if user_id_str not in self.data:
            self.data[user_id_str] = {
                'first_seen': datetime.now().isoformat(),
                'last_active': datetime.now().isoformat(),
                'total_actions': 0
            }
            self._save_data()

    def update_activity(self, user_id: int) -> None:
        """Обновляет время последней активности пользователя"""
        user_id_str = str(user_id)
        now = datetime.now().isoformat()

        if user_id_str not in self.data:
            self.register_user(user_id)
        else:
            self.data[user_id_str]['last_active'] = now
            self.data[user_id_str]['total_actions'] += 1
            self._save_data()

    def get_total_users(self) -> int:
        """Возвращает общее количество зарегистрированных пользователей"""
        return len(self.data)

    def get_active_users_count(self, days: int = 7) -> int:
        """Возвращает количество активных пользователей за указанный период"""
        threshold = datetime.now() - timedelta(days=days)
        count = 0

        for user_data in self.data.values():
            last_active = datetime.fromisoformat(user_data['last_active'])
            if last_active >= threshold:
                count += 1

        return count

    def get_user_activity(self, user_id: int) -> Optional[dict]:
        """Возвращает данные о активности конкретного пользователя"""
        user_id_str = str(user_id)
        return self.data.get(user_id_str)

    def cleanup_inactive_users(self, days: int = 365) -> None:
        """Удаляет данные о пользователях, неактивных более указанного периода"""
        threshold = datetime.now() - timedelta(days=days)
        inactive_users = [
            user_id for user_id, user_data in self.data.items()
            if datetime.fromisoformat(user_data['last_active']) < threshold
        ]

        for user_id in inactive_users:
            del self.data[user_id]

        if inactive_users:
            self._save_data()
            logger.info(f"Removed {len(inactive_users)} inactive users")
