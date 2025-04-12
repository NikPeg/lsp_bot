"""
Модуль обработчиков для административных команд.
Содержит команды для получения статистики о пользователях бота.
"""

from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import Command, ChatTypeFilter
from aiogram.types import Message
from loguru import logger

from app.config import settings
from app.services.user_service import UserService

# Создаем роутер для административных команд
admin_router = Router()
admin_router.message.filter(
    ChatTypeFilter(chat_type=["group", "supergroup"]),
    F.chat.id == settings.ADMIN_GROUP_ID
)

# Сервис для работы с данными пользователей
user_service = UserService()


@admin_router.message(Command("users_count"))
async def cmd_users_count(message: Message):
    """
    Обработчик команды для получения количества уникальных пользователей.

    Args:
        message (Message): Сообщение с командой.
    """
    try:
        # Получаем общее количество пользователей
        users_count = await user_service.get_total_users_count()

        await message.answer(
            f"📊 Общее количество пользователей, запустивших бота: {users_count}"
        )
        logger.info(f"Запрошена статистика по количеству пользователей: {users_count}")
    except Exception as e:
        logger.error(f"Ошибка при получении статистики пользователей: {e}")
        await message.answer("❌ Произошла ошибка при получении статистики.")


@admin_router.message(Command("active_users"))
async def cmd_active_users(message: Message):
    """
    Обработчик команды для получения количества активных пользователей за последнюю неделю.

    Args:
        message (Message): Сообщение с командой.
    """
    try:
        # Определяем дату неделю назад
        week_ago = datetime.now() - timedelta(days=7)

        # Получаем количество активных пользователей
        active_users_count = await user_service.get_active_users_count(since=week_ago)

        await message.answer(
            f"📈 Количество активных пользователей за последнюю неделю: {active_users_count}"
        )
