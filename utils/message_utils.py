from aiogram.types import Message, FSInputFile
import os
from typing import Optional, Union
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

async def send_message_with_image(
        message: Message,
        text: str,
        image_path: str,
        reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = None
) -> Message:
    """
    Отправляет сообщение с изображением

    Аргументы:
        message (Message): Объект сообщения для ответа
        text (str): Текст сообщения
        image_path (str): Путь к изображению
        reply_markup (Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]]): Клавиатура

    Возвращает:
        Message: Объект отправленного сообщения
    """
    # Проверяем существование файла
    if not os.path.exists(image_path):
        # Если изображение не найдено, отправляем только текст
        return await message.answer(text=text, reply_markup=reply_markup)

    # Создаем объект FSInputFile для изображения
    photo = FSInputFile(image_path)

    # Отправляем сообщение с изображением
    return await message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=reply_markup
    )
