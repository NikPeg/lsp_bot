import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.handlers import (
    common,
    language,
    profile,
    learning_center,
    schedule,
    faculty,
    subjects,
    materials,
    admin
)
from config import get_config
from bot.middleware import (
    LanguageMiddleware,
    AntiForwardMiddleware,
    ActivityMiddleware
)
from bot.services import user_activity
from bot.utils import setup_logging

config = get_config()

async def main():
    # Настройка логирования
    setup_logging()

    # Инициализация бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Подключение middleware
    dp.message.middleware(LanguageMiddleware())
    dp.callback_query.middleware(LanguageMiddleware())
    dp.message.middleware(AntiForwardMiddleware())
    dp.update.middleware(ActivityMiddleware(user_activity))

    # Регистрация роутеров
    dp.include_router(common.router)
    dp.include_router(language.router)
    dp.include_router(profile.router)
    dp.include_router(learning_center.router)
    dp.include_router(schedule.router)
    dp.include_router(faculty.router)
    dp.include_router(subjects.router)
    dp.include_router(materials.router)
    dp.include_router(admin.router)

    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
