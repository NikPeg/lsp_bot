from aiogram import Dispatcher, types
from aiogram.types import InlineKeyboardMarkup
import os

from keyboards.learning_kb import get_navigation_keyboard
from keyboards.inline_kb import get_back_keyboard, get_after_file_keyboard

from database.db_manager import get_user_faculty, get_user_language

from services.text_manager import get_text
from services.file_manager import get_directories, get_files, check_file_exists

from utils.helpers import get_parent_path, format_path, is_image_file
from utils.emoji import add_emoji_to_text

from config import MATERIALS_FOLDER

async def learning_handler(message: types.Message):
    """
    Обработчик нажатия на кнопку "Центр обучения"
    """
    user_id = message.from_user.id
    user_language = message.data.get('user_language', 'ru')

    # Получаем текущий факультет пользователя
    faculty = await get_user_faculty(user_id)

    if not faculty:
        # Если факультет не выбран, предлагаем пользователю сначала выбрать факультет
        text = get_text(user_language, "please_select_faculty")
        await message.answer(text)
        return await message.forward(lambda: profile_handler(message))

    # Формируем путь к материалам факультета
    faculty_path = os.path.join(MATERIALS_FOLDER, faculty)

    # Получаем текст для центра обучения
    learning_center_text = get_text(user_language, "learning_center_text")
    faculty_text = get_text(user_language, f"faculty_{faculty.split()[0][0]}_name", default=faculty)

    # Формируем текст сообщения с выбранным факультетом
    text = f"{learning_center_text}\n\n{get_text(user_language, 'current_faculty').format(faculty=faculty_text)}"

    # Получаем клавиатуру для навигации
    keyboard = await get_navigation_keyboard(user_language, faculty_path)

    # Отправляем сообщение с навигацией
    await message.answer(
        text=text,
        reply_markup=keyboard
    )

async def navigate_callback(callback_query: types.CallbackQuery, callback_data: dict):
    """
    Обработчик навигации по папкам с материалами
    """
    user_language = callback_query.data.get('user_language', 'ru')
    path = callback_data["value"]

    # Получаем родительский путь
    parent_path = get_parent_path(path)

    # Получаем имя текущей директории для отображения
    dir_name = os.path.basename(path) or path

    # Пытаемся найти перевод для названия директории
    dir_key = f"dir_{dir_name.replace(' ', '_').lower()}"
    dir_text = get_text(user_language, dir_key, default=dir_name)

    # Формируем текст с выбранной директорией
    text = f"{get_text(user_language, 'select_material_type')}: {dir_text}\n\n"
    text += f"{format_path(path)}"

    # Проверяем наличие папок и файлов в директории
    directories = await get_directories(path)
    files = await get_files(path)

    if not directories and not files:
        # Если папка пуста, сообщаем об этом
        text += f"\n\n{get_text(user_language, 'no_materials_found_in_semester')}"

    # Получаем клавиатуру для навигации
    keyboard = await get_navigation_keyboard(user_language, path, parent_path)

    # Отвечаем на callback и обновляем сообщение
    await callback_query.answer()
    await callback_query.message.edit_text(
        text=text,
        reply_markup=keyboard
    )

async def download_file_callback(callback_query: types.CallbackQuery, callback_data: dict):
    """
    Обработчик скачивания файла
    """
    user_language = callback_query.data.get('user_language', 'ru')
    file_path = callback_data["value"]

    # Проверяем существование файла
    if not await check_file_exists(file_path):
        await callback_query.answer(get_text(user_language, "file_not_found"), show_alert=True)
        return

    # Отправляем сообщение о загрузке файла
    loading_text = get_text(user_language, "loading_file")
    await callback_query.answer(loading_text)

    # Получаем имя файла
    file_name = os.path.basename(file_path)

    try:
        # Проверяем, является ли файл изображением
        if is_image_file(file_name):
            # Отправляем файл как фото
            with open(file_path, 'rb') as photo:
                await callback_query.message.answer_photo(
                    photo=photo,
                    caption=file_name,
                    reply_markup=get_after_file_keyboard(user_language)
                )
        else:
            # Отправляем файл как документ
            with open(file_path, 'rb') as document:
                await callback_query.message.answer_document(
                    document=document,
                    caption=file_name,
                    reply_markup=get_after_file_keyboard(user_language)
                )
    except Exception as e:
        # В случае ошибки сообщаем пользователю
        await callback_query.message.answer(
            text=f"{get_text(user_language, 'error_sending_file')}: {str(e)}",
            reply_markup=get_back_keyboard(user_language, "back_to_materials")
        )

async def back_to_materials_callback(callback_query: types.CallbackQuery):
    """
    Обработчик возврата к материалам после скачивания файла
    """
    user_id = callback_query.from_user.id
    user_language = callback_query.data.get('user_language', 'ru')

    # Получаем текущий факультет пользователя
    faculty = await get_user_faculty(user_id)

    if not faculty:
        # Если факультет не выбран, возвращаемся в главное меню
        await callback_query.answer()
        return await callback_query.forward(lambda: back_to_main_callback(callback_query))

    # Формируем путь к материалам факультета
    faculty_path = os.path.join(MATERIALS_FOLDER, faculty)

    # Получаем текст для центра обучения
    learning_center_text = get_text(user_language, "learning_center_text")
    faculty_text = get_text(user_language, f"faculty_{faculty.split()[0][0]}_name", default=faculty)

    # Формируем текст сообщения с выбранным факультетом
    text = f"{learning_center_text}\n\n{get_text(user_language, 'current_faculty').format(faculty=faculty_text)}"

    # Получаем клавиатуру для навигации
    keyboard = await get_navigation_keyboard(user_language, faculty_path)

    # Отвечаем на callback и обновляем сообщение
    await callback_query.answer()
    await callback_query.message.edit_text(
        text=text,
        reply_markup=keyboard
    )

def register_learning_handlers(dp: Dispatcher):
    """
    Регистрирует обработчики для центра обучения
    """
    dp.register_message_handler(
        learning_handler,
        lambda message: message.text.startswith("📚")
    )

    dp.register_callback_query_handler(
        navigate_callback,
        lambda c: c.data.startswith("navigate:"),
        lambda c: {"value": c.data.split(":")[1]}
    )

    dp.register_callback_query_handler(
        download_file_callback,
        lambda c: c.data.startswith("download:"),
        lambda c: {"value": c.data.split(":")[1]}
    )

    dp.register_callback_query_handler(
        back_to_materials_callback,
        lambda c: c.data == "back_to_materials"
    )
