from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup

from keyboards.main_kb import get_main_keyboard
from services.text_manager import get_text
from utils.emoji import add_emoji_to_text
from config import UNKNOWN_COMMAND

async def process_main_menu(message: types.Message):
    """
    Обработчик текстовых сообщений в главном меню
    """
    user_language = message.data.get('user_language', 'ru')
    text = message.text

    # Получаем тексты кнопок на языке пользователя
    profile_text = add_emoji_to_text("👤", get_text(user_language, "profile_button"))
    learning_text = add_emoji_to_text("📚", get_text(user_language, "learning_center_button"))
    schedule_text = add_emoji_to_text("📆", get_text(user_language, "schedule_button"))
    channel_text = add_emoji_to_text("📢", get_text(user_language, "channel_button"))

    # Проверяем, какая кнопка была нажата
    if text == profile_text:
        # Перенаправляем на обработчик профиля
        return await message.forward(lambda: profile_handler(message))

    elif text == learning_text:
        # Перенаправляем на обработчик центра обучения
        return await message.forward(lambda: learning_handler(message))

    elif text == schedule_text:
        # Перенаправляем на обработчик расписания
        return await message.forward(lambda: schedule_handler(message))

    elif text == channel_text:
        # Перенаправляем на обработчик канала
        return await message.forward(lambda: channel_handler(message))

    else:
        # Если сообщение не соответствует ни одной кнопке, отправляем сообщение о неизвестной команде
        unknown_command_text = UNKNOWN_COMMAND.get(user_language)
        await message.answer(unknown_command_text)

async def back_to_main_callback(callback_query: types.CallbackQuery):
    """
    Обработчик возврата в главное меню из других разделов
    """
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

def register_main_menu_handlers(dp: Dispatcher):
    """
    Регистрирует обработчики для главного меню
    """
    dp.register_message_handler(process_main_menu)
    dp.register_callback_query_handler(
        back_to_main_callback,
        lambda c: c.data == "back_to_main"
    )
