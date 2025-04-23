import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

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
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Middleware для обновления активности пользователя
class ActivityMiddleware:
    async def __call__(self, handler, event, data):
        if isinstance(event, types.Message):
            await update_user_activity(event.from_user.id)
        elif isinstance(event, types.CallbackQuery):
            await update_user_activity(event.from_user.id)

        return await handler(event, data)

async def on_startup():
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
    dp.message.middleware(ActivityMiddleware())
    dp.callback_query.middleware(ActivityMiddleware())

    logger.info("Bot started successfully!")

async def main():
    """
    Главная функция запуска бота
    """
    # Устанавливаем обработчик события запуска
    dp.startup.register(on_startup)

    # Запускаем бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        # Запускаем главную функцию
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Обрабатываем случай, когда пользователь прерывает бота
        logger.info("Bot stopped!")
