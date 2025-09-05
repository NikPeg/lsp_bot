import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError

from config import BOT_TOKEN
from handlers import register_all_handlers
from middlewares import setup_middleware
from database.models import init_db
from database.db_manager import update_user_activity
from config import DATABASE_PATH
from utils.file_handler import cleanup_temp_files

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создание экземпляра бота и диспетчера с новым синтаксисом для 3.7.0+
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
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

    # Очищаем временные файлы при запуске
    cleanup_temp_files()

    logger.info("Bot started successfully!")

async def global_error_handler(update: types.Update, exception: Exception):
    """
    Глобальный обработчик ошибок для graceful обработки исключений
    """
    logger.error(f"Unhandled exception in update {update}: {exception}", exc_info=True)
    
    # Обрабатываем специфичные ошибки Telegram
    if isinstance(exception, TelegramBadRequest):
        if "message is not modified" in str(exception):
            logger.debug("Ignored 'message is not modified' error")
            return True  # Игнорируем эту ошибку
        elif "message to edit not found" in str(exception):
            logger.debug("Ignored 'message to edit not found' error")
            return True
    elif isinstance(exception, TelegramNetworkError):
        logger.warning(f"Network error: {exception}")
        return True  # Продолжаем работу при сетевых ошибках
    
    # Для остальных ошибок логируем и продолжаем
    return True

async def main():
    """
    Главная функция запуска бота
    """
    # Устанавливаем обработчик события запуска
    dp.startup.register(on_startup)
    
    # Регистрируем глобальный обработчик ошибок
    dp.errors.register(global_error_handler)

    # Запускаем бота
    try:
        logger.info("Starting bot polling...")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error in main loop: {e}", exc_info=True)
        raise
    finally:
        logger.info("Closing bot session...")
        await bot.session.close()

if __name__ == "__main__":
    try:
        # Запускаем главную функцию
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Обрабатываем случай, когда пользователь прерывает бота
        logger.info("Bot stopped!")
