from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import os

from keyboards.schedule_kb import get_schedule_keyboard
from keyboards.inline_kb import get_back_keyboard

from services.text_manager import get_text
from utils.emoji import add_emoji_to_text

from config import IMAGES_FOLDER

# Создаем роутер для обработчиков расписания
router = Router()

@router.message(F.text.startswith("📆"))
async def schedule_handler(message: Message):
    """
    Обработчик нажатия на кнопку "Расписание"
    """
    user_language = message.data.get('user_language', 'ru')

    # Получаем текст для расписания
    schedule_text = get_text(user_language, "schedule_text")

    # Получаем клавиатуру для выбора типа расписания
    keyboard = get_schedule_keyboard(user_language)

    # Отправляем сообщение с выбором типа расписания
    await message.answer(
        text=schedule_text,
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("schedule:"))
async def schedule_type_callback(callback_query: CallbackQuery):
    """
    Обработчик выбора типа расписания
    """
    user_language = callback_query.data.get('user_language', 'ru')
    schedule_type = callback_query.data.split(":")[1]

    # Формируем путь к изображению
    image_path = os.path.join(IMAGES_FOLDER, f"{schedule_type}.png")

    # Получаем текст для выбранного типа расписания
    schedule_text_key = f"{schedule_type}_schedule_text"
    schedule_text = get_text(user_language, schedule_text_key)

    # Отвечаем на callback
    await callback_query.answer()

    try:
        # Проверяем существование файла
        if not os.path.exists(image_path):
            await callback_query.message.edit_text(
                text=f"{get_text(user_language, 'image_not_found')}",
                reply_markup=get_back_keyboard(user_language, "back_to_schedule")
            )
            return

        # Отправляем изображение расписания
        with open(image_path, 'rb') as photo:
            # Сначала отвечаем на callback и обновляем сообщение
            await callback_query.message.edit_text(schedule_text)

            # Затем отправляем изображение
            await callback_query.message.answer_photo(
                photo=photo,
                caption=schedule_text,
                reply_markup=get_back_keyboard(user_language, "back_to_schedule")
            )

    except Exception as e:
        # В случае ошибки сообщаем пользователю
        await callback_query.message.edit_text(
            text=f"{get_text(user_language, 'error_sending_image')}: {str(e)}",
            reply_markup=get_back_keyboard(user_language, "back_to_schedule")
        )

@router.callback_query(F.data == "back_to_schedule")
async def back_to_schedule_callback(callback_query: CallbackQuery):
    """
    Обработчик возврата к выбору типа расписания
    """
    user_language = callback_query.data.get('user_language', 'ru')

    # Получаем текст для расписания
    schedule_text = get_text(user_language, "schedule_text")

    # Получаем клавиатуру для выбора типа расписания
    keyboard = get_schedule_keyboard(user_language)

    # Отвечаем на callback и обновляем сообщение
    await callback_query.answer()
    await callback_query.message.edit_text(
        text=schedule_text,
        reply_markup=keyboard
    )

def setup_schedule_handlers(dp):
    """
    Регистрирует обработчики для раздела с расписанием
    """
    dp.include_router(router)
