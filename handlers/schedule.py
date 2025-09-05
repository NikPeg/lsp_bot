from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.exceptions import TelegramBadRequest
import os

from keyboards.schedule_kb import get_schedule_keyboard
from keyboards.inline_kb import get_back_keyboard

from services.text_manager import get_text
from utils.emoji import add_emoji_to_text
from utils.message_edit_utils import safe_edit_text

from config import IMAGES_FOLDER, DEFAULT_LANGUAGE
from config import INTERFACE_IMAGES_FOLDER, IMAGES_FOLDER
from utils.message_utils import send_message_with_image
# Создаем роутер для обработчиков расписания
router = Router()

@router.message(F.text.startswith("📆"))
async def schedule_handler(message: Message, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик нажатия на кнопку "Расписание"
    """
    # Получаем текст для расписания
    schedule_text = get_text(user_language, "schedule_text")

    # Получаем клавиатуру для выбора типа расписания
    keyboard = get_schedule_keyboard(user_language)

    # Путь к изображению
    image_path = os.path.join(INTERFACE_IMAGES_FOLDER, "schedule.png")

    # Отправляем сообщение с изображением
    await send_message_with_image(
        message=message,
        text=schedule_text,
        image_path=image_path,
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("schedule:"))
async def schedule_type_callback(callback_query: CallbackQuery, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик выбора типа расписания
    """
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
            # Пытаемся удалить предыдущее сообщение
            try:
                await callback_query.message.delete()
            except Exception as e:
                print(f"Error deleting message: {e}")

            # Отправляем сообщение об отсутствии изображения
            await callback_query.message.answer(
                text=f"{get_text(user_language, 'image_not_found')}",
                reply_markup=get_back_keyboard(user_language, "back_to_schedule")
            )
            return

        # Пытаемся удалить предыдущее сообщение
        try:
            await callback_query.message.delete()
        except Exception as e:
            print(f"Error deleting message: {e}")

        # Создаем объект FSInputFile для изображения
        photo = FSInputFile(image_path)

        # Отправляем новое сообщение с изображением
        await callback_query.message.answer_photo(
            photo=photo,
            caption=schedule_text,
            reply_markup=get_back_keyboard(user_language, "back_to_schedule")
        )

    except Exception as e:
        # В случае ошибки сообщаем пользователю
        # Пытаемся удалить предыдущее сообщение
        try:
            await callback_query.message.delete()
        except Exception as delete_error:
            print(f"Error deleting message: {delete_error}")

        await callback_query.message.answer(
            text=f"{get_text(user_language, 'error_sending_image')}: {str(e)}",
            reply_markup=get_back_keyboard(user_language, "back_to_schedule")
        )

@router.callback_query(F.data == "back_to_schedule")
async def back_to_schedule_callback(callback_query: CallbackQuery, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик возврата к выбору типа расписания
    """
    # Получаем текст для расписания
    schedule_text = get_text(user_language, "schedule_text")

    # Получаем клавиатуру для выбора типа расписания
    keyboard = get_schedule_keyboard(user_language)

    # Отвечаем на callback
    await callback_query.answer()

    # Используем безопасное редактирование текста
    edited = await safe_edit_text(callback_query, schedule_text, keyboard)
    if not edited:
        # Если не получается отредактировать (например, если это фото),
        # удаляем текущее сообщение и отправляем новое
        try:
            await callback_query.message.delete()
        except Exception:
            # Если не удалось удалить, просто игнорируем ошибку
            pass

        # Отправляем новое сообщение
        await callback_query.message.answer(
            text=schedule_text,
            reply_markup=keyboard
        )

def setup_schedule_handlers(dp):
    """
    Регистрирует обработчики для раздела с расписанием
    """
    dp.include_router(router)
