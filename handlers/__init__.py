from handlers.start import register_start_handlers
from handlers.main_menu import register_main_menu_handlers
from handlers.profile import register_profile_handlers
from handlers.learning import register_learning_handlers
from handlers.schedule import register_schedule_handlers
from handlers.channel import register_channel_handlers

def register_all_handlers(dp):
    """
    Регистрирует все обработчики сообщений
    """
    register_start_handlers(dp)
    register_profile_handlers(dp)
    register_learning_handlers(dp)
    register_schedule_handlers(dp)
    register_channel_handlers(dp)

    # Регистрируем обработчик main_menu последним,
    # чтобы он обрабатывал только сообщения, которые не были обработаны другими обработчиками
    register_main_menu_handlers(dp)

__all__ = ['register_all_handlers']
