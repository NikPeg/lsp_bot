from middlewares.i18n import I18nMiddleware

def setup_middleware(dp):
    """
    Устанавливает middleware для диспетчера
    """
    # Устанавливаем middleware для всех типов сообщений
    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())

__all__ = ['setup_middleware']
