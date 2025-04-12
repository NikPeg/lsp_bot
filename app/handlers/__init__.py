import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.handlers import (
    start,
    main_menu,
    profile,
    learning_center,
    schedule,
    faculty,
    materials,
    admin
)
from app.config import get_config
from app.middleware import (
    LanguageMiddleware,
    AntiForwardMiddleware,
    ActivityTrackerMiddleware
)
from app.services import user_activity

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение конфигурации
config = get_config()

async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Подключение middleware
    dp.message.middleware(LanguageMiddleware())
    dp.callback_query.middleware(LanguageMiddleware())
    dp.message.middleware(AntiForwardMiddleware())
    dp.update.middleware(ActivityTrackerMiddleware())

    # Регистрация роутеров в правильном порядке
    dp.include_router(start.start_router)
    dp.include_router(main_menu.router)
    dp.include_router(profile.router)
    dp.include_router(learning_center.router)
    dp.include_router(faculty.router)
    dp.include_router(materials.router)
    dp.include_router(schedule.router)
    dp.include_router(admin.router)

    # Запуск бота
    try:
        logger.info("Starting bot...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
