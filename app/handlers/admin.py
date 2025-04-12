"""
Модуль обработчиков для административных команд.
Содержит команды для получения статистики о пользователях бота.
"""

from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ChatType
from loguru import logger

from config import get_config
from bot.services import user_activity

# Получаем конфигурацию
config = get_config()

# Создаем роутер для административных команд
admin_router = Router()
admin_router.message.filter(
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
    F.chat.id == config.ADMIN_GROUP_ID
)

@admin_router.message(Command("users_count"))
async def cmd_users_count(message: Message):
    """
    Обработчик команды для получения количества уникальных пользователей.
    """
    try:
        users_count = user_activity.get_total_users()
        await message.answer(
            f"📊 Общее количество пользователей: {users_count}"
        )
        logger.info(f"Admin requested users count: {users_count}")
    except Exception as e:
        logger.error(f"Error getting users count: {e}")
        await message.answer("❌ Ошибка при получении статистики")

@admin_router.message(Command("active_users"))
async def cmd_active_users(message: Message):
    """
    Обработчик команды для получения количества активных пользователей за неделю.
    """
    try:
        active_count = user_activity.get_active_users_count(days=7)
        await message.answer(
            f"📈 Активных пользователей за неделю: {active_count}"
        )
        logger.info(f"Admin requested active users: {active_count}")
    except Exception as e:
        logger.error(f"Error getting active users: {e}")
        await message.answer("❌ Ошибка при получении статистики")

@admin_router.message(Command("cleanup"))
async def cmd_cleanup_users(message: Message):
    """
    Очистка неактивных пользователей (неактивные более года)
    """
    try:
        user_activity.cleanup_inactive_users(days=365)
        await message.answer("✅ Очистка неактивных пользователей выполнена")
        logger.info("Admin performed inactive users cleanup")
    except Exception as e:
        logger.error(f"Error cleaning inactive users: {e}")
        await message.answer("❌ Ошибка при очистке пользователей")
