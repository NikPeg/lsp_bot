import asyncio
from aiogram import Bot
from config import ADMIN_GROUP_ID
import logging

logger = logging.getLogger(__name__)

async def send_admin_log(bot: Bot, message: str):
    """
    Отправляет лог-сообщение в админскую группу
    
    Args:
        bot: Экземпляр бота
        message: Сообщение для отправки
    """
    if not ADMIN_GROUP_ID:
        logger.warning("ADMIN_GROUP_ID не настроен, лог не отправлен")
        return
    
    try:
        await bot.send_message(
            chat_id=ADMIN_GROUP_ID,
            text=f"📊 {message}",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки лога в админскую группу: {e}")

def format_user_info(user):
    """
    Форматирует информацию о пользователе для логов
    
    Args:
        user: Объект пользователя Telegram
        
    Returns:
        str: Отформатированная строка с информацией о пользователе
    """
    username = f"@{user.username}" if user.username else "без username"
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    return f"{full_name} ({username}, ID: {user.id})"

async def log_bot_start(bot: Bot, user):
    """
    Логирует запуск бота пользователем
    """
    user_info = format_user_info(user)
    message = f"🚀 Пользователь {user_info} запустил бота"
    await send_admin_log(bot, message)

async def log_faculty_selection(bot: Bot, user, faculty):
    """
    Логирует выбор факультета пользователем
    """
    user_info = format_user_info(user)
    message = f"🎓 Пользователь {user_info} выбрал факультет: <b>{faculty}</b>"
    await send_admin_log(bot, message)

async def log_file_download(bot: Bot, user, filename):
    """
    Логирует скачивание файла пользователем
    """
    user_info = format_user_info(user)
    message = f"📁 Пользователь {user_info} скачал файл: <b>{filename}</b>"
    await send_admin_log(bot, message)