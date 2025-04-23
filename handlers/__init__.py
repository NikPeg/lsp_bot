from handlers.start import setup_start_handlers
from handlers.main_menu import setup_main_menu_handlers
from handlers.profile import setup_profile_handlers
from handlers.learning import setup_learning_handlers
from handlers.schedule import setup_schedule_handlers
from handlers.channel import setup_channel_handlers

def register_all_handlers(dp):
    """
    Регистрирует все обработчики сообщений
    """
    # Регистрируем обработчики в порядке приоритета
    setup_start_handlers(dp)
    setup_profile_handlers(dp)
    setup_learning_handlers(dp)
    setup_schedule_handlers(dp)
    setup_channel_handlers(dp)

    # Регистрируем обработчик main_menu последним,
    # чтобы он обрабатывал только сообщения, которые не были обработаны другими обработчиками
    setup_main_menu_handlers(dp)

__all__ = ['register_all_handlers']
