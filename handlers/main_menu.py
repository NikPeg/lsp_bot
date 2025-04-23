from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.main_kb import get_main_keyboard
from services.text_manager import get_text
from utils.emoji import add_emoji_to_text
from config import UNKNOWN_COMMAND

# Создаем роутер для обработчиков главного меню
router = Router()

@router.message()
async def process_main_menu(message: Message):
    """
    Обработчик текстовых сообщений в главном меню
    """
    # Получаем язык пользователя из middleware
    user_language = message.data.get('user_language', 'ru')
    text = message.text

    # Получаем тексты кнопок на языке пользователя
    profile_text = add_emoji_to_text("👤", get_text(user_language, "profile_button"))
    learning_text = add_emoji_to_text("📚", get_text(user_language, "learning_center_button"))
    schedule_text = add_emoji_to_text("📆", get_text(user_language, "schedule_button"))
    channel_text = add_emoji_to_text("📢", get_text(user_language, "channel_button"))

    # Проверяем, какая кнопка была нажата
    if text == profile_text:
        # Перенаправляем на обработчик профиля (логика будет в другом обработчике)
        from handlers.profile import profile_handler
        return await profile_handler(message)

    elif text == learning_text:
        # Перенаправляем на обработчик центра обучения
        from handlers.learning import learning_handler
        return await learning_handler(message)

    elif text == schedule_text:
        # Перенаправляем на обработчик расписания
        from handlers.schedule import schedule_handler
        return await schedule_handler(message)

    elif text == channel_text:
        # Перенаправляем на обработчик канала
        from handlers.channel import channel_handler
        return await channel_handler(message)

    else:
        # Если сообщение не соответствует ни одной кнопке, отправляем сообщение о неизвестной команде
        unknown_command_text = UNKNOWN_COMMAND.get(user_language)
        await message.answer(unknown_command_text)

@router.callback_query(F.data == "back_to_main")
async def back_to_main_callback(callback_query: CallbackQuery):
    """
    Обработчик возврата в главное меню из других разделов
    """
    # Получаем язык пользователя из middleware
    user_language = callback_query.data.get('user_language', 'ru')

    # Получаем текст главного меню на языке пользователя
    main_menu_text = get_text(user_language, "main_menu_text")

    # Получаем клавиатуру главного меню
    main_keyboard = get_main_keyboard(user_language)

    # Отвечаем на callback и обновляем сообщение
    await callback_query.answer()
    await callback_query.message.edit_text(main_menu_text)

    # Отправляем новое сообщение с главным меню, если нужно
    await callback_query.message.answer(
        text=main_menu_text,
        reply_markup=main_keyboard
    )

def setup_main_menu_handlers(dp):
    """
    Регистрирует обработчики для главного меню
    """
    dp.include_router(router)
