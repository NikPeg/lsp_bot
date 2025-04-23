import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import register_all_handlers
from middlewares import setup_middleware
from database.models import init_db
from database.db_manager import update_user_activity
from config import DATABASE_PATH

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создание экземпляра бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Middleware для обновления активности пользователя
class ActivityMiddleware:
    async def on_pre_process_message(self, message: types.Message, data: dict):
        await update_user_activity(message.from_user.id)

    async def on_pre_process_callback_query(self, query: types.CallbackQuery, data: dict):
        await update_user_activity(query.from_user.id)

async def on_startup(dp: Dispatcher):
    """
    Действия, выполняемые при запуске бота
    """
    logger.info("Starting bot...")

    # Инициализируем базу данных
    init_db(DATABASE_PATH)

    # Настраиваем обработчики и middleware
    register_all_handlers(dp)
    setup_middleware(dp)

    # Добавляем middleware для отслеживания активности
    dp.middleware.setup(ActivityMiddleware())

    logger.info("Bot started successfully!")

async def on_shutdown(dp: Dispatcher):
    """
    Действия, выполняемые при завершении работы бота
    """
    logger.info("Shutting down...")

    # Закрываем хранилище состояний
    await dp.storage.close()
    await dp.storage.wait_closed()

    logger.info("Bot shutdown complete!")

async def main():
    """
    Главная функция запуска бота
    """
    # Устанавливаем обработчики событий запуска и завершения
    dp.register_on_startup_callback(on_startup)
    dp.register_on_shutdown_callback(on_shutdown)

    # Запускаем бота
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()

if __name__ == "__main__":
    try:
        # Запускаем главную функцию
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Обрабатываем случай, когда пользователь прерывает бота
        logger.info("Bot stopped!")
