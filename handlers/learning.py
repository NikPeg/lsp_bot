from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import os

from keyboards.learning_kb import get_navigation_keyboard
from keyboards.inline_kb import get_back_keyboard, get_after_file_keyboard

from database.db_manager import get_user_faculty, get_user_language
from config import INTERFACE_IMAGES_FOLDER, MATERIALS_FOLDER
from utils.message_utils import send_message_with_image
import os
from services.text_manager import get_text
from services.file_manager import get_directories, get_files, check_file_exists

from utils.helpers import get_parent_path, format_path, is_image_file
from utils.emoji import add_emoji_to_text
from aiogram.types import Message, CallbackQuery, FSInputFile

from config import MATERIALS_FOLDER, DEFAULT_LANGUAGE
from utils.file_handler import send_large_file
from utils.admin_logger import log_file_download

# Создаем роутер для обработчиков центра обучения
router = Router()

@router.message(F.text.startswith("📚"))
async def learning_handler(message: Message, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик нажатия на кнопку "Центр обучения"
    """
    user_id = message.from_user.id

    # Получаем текущий факультет пользователя
    faculty = await get_user_faculty(user_id)

    if not faculty:
        # Если факультет не выбран, предлагаем пользователю сначала выбрать факультет
        text = get_text(user_language, "please_select_faculty")
        await message.answer(text)
        # Перенаправление на профиль для выбора факультета
        from handlers.profile import profile_handler
        return await profile_handler(message, user_language=user_language)

    # Формируем путь к материалам факультета
    faculty_path = os.path.join(MATERIALS_FOLDER, faculty)

    # Получаем текст для центра обучения
    learning_center_text = get_text(user_language, "learning_center_text")
    faculty_text = get_text(user_language, f"faculty_{faculty.split()[0][0]}_name", default=faculty)

    # Формируем текст сообщения с выбранным факультетом
    text = f"{learning_center_text}\n\n{get_text(user_language, 'current_faculty').format(faculty=faculty_text)}"

    # Получаем клавиатуру для навигации
    keyboard = await get_navigation_keyboard(user_language, faculty_path)

    # Путь к изображению
    image_path = os.path.join(INTERFACE_IMAGES_FOLDER, "learning.png")

    # Отправляем сообщение с изображением
    await send_message_with_image(
        message=message,
        text=text,
        image_path=image_path,
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("nav:"))
async def navigate_callback(callback_query: CallbackQuery, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик навигации по папкам с материалами
    """
    # Получаем идентификатор пути и восстанавливаем полный путь
    path_id = callback_query.data.split(":")[1]
    from keyboards.learning_kb import get_path_by_id
    path = get_path_by_id(path_id)

    if not path:
        await callback_query.answer("Путь не найден", show_alert=True)
        return

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
    await callback_query.message.delete()
    await callback_query.message.answer(
        text=text,
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("dl:"))
async def download_file_callback(callback_query: CallbackQuery, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик скачивания файла с поддержкой больших файлов
    """
    # Получаем идентификатор пути и восстанавливаем полный путь к файлу
    path_id = callback_query.data.split(":")[1]
    from keyboards.learning_kb import get_path_by_id
    file_path = get_path_by_id(path_id)

    if not file_path:
        await callback_query.answer("Файл не найден", show_alert=True)
        return

    # Проверяем существование файла
    if not await check_file_exists(file_path):
        await callback_query.answer(get_text(user_language, "file_not_found"), show_alert=True)
        return

    # Отправляем сообщение о загрузке файла
    loading_text = get_text(user_language, "loading_file")
    await callback_query.answer(loading_text)

    # Получаем имя файла
    file_name = os.path.basename(file_path)
    
    # Получаем бота из callback_query
    bot = callback_query.bot
    chat_id = callback_query.message.chat.id

    try:
        # Проверяем, является ли файл изображением
        is_photo = is_image_file(file_name)
        
        # Используем новую функцию для отправки больших файлов
        success, message = await send_large_file(
            bot=bot,
            chat_id=chat_id,
            file_path=file_path,
            caption=file_name,
            is_photo=is_photo,
            language=user_language
        )
        
        if success:
            # Логируем скачивание файла
            await log_file_download(callback_query.bot, callback_query.from_user, file_name)
            
            # Отправляем клавиатуру после успешной отправки файла
            await callback_query.message.answer(
                text=message,
                reply_markup=get_after_file_keyboard(user_language)
            )
        else:
            # В случае ошибки сообщаем пользователю
            await callback_query.message.answer(
                text=f"{get_text(user_language, 'error_sending_file')}: {message}",
                reply_markup=get_back_keyboard(user_language, "back_to_materials")
            )
            
    except Exception as e:
        # В случае неожиданной ошибки сообщаем пользователю
        await callback_query.message.answer(
            text=f"{get_text(user_language, 'error_sending_file')}: {str(e)}",
            reply_markup=get_back_keyboard(user_language, "back_to_materials")
        )

@router.callback_query(F.data == "back_to_materials")
async def back_to_materials_callback(callback_query: CallbackQuery, user_language: str = DEFAULT_LANGUAGE):
    """
    Обработчик возврата к материалам после скачивания файла
    """
    user_id = callback_query.from_user.id

    # Получаем текущий факультет пользователя
    faculty = await get_user_faculty(user_id)

    if not faculty:
        # Если факультет не выбран, возвращаемся в главное меню
        await callback_query.answer()
        from handlers.main_menu import back_to_main_callback
        return await back_to_main_callback(callback_query, user_language=user_language)

    # Формируем путь к материалам факультета
    faculty_path = os.path.join(MATERIALS_FOLDER, faculty)

    # Получаем текст для центра обучения
    learning_center_text = get_text(user_language, "learning_center_text")
    faculty_text = get_text(user_language, f"faculty_{faculty.split()[0][0]}_name", default=faculty)

    # Формируем текст сообщения с выбранным факультетом
    text = f"{learning_center_text}\n\n{get_text(user_language, 'current_faculty').format(faculty=faculty_text)}"

    # Получаем клавиатуру для навигации
    keyboard = await get_navigation_keyboard(user_language, faculty_path)

    # Отвечаем на callback
    await callback_query.answer()

    try:
        # Пробуем отредактировать текущее сообщение
        await callback_query.message.edit_text(
            text=text,
            reply_markup=keyboard
        )
    except Exception:
        # Если не получается отредактировать, удаляем текущее сообщение и отправляем новое
        try:
            await callback_query.message.delete()
        except Exception:
            # Если не удалось удалить, просто игнорируем ошибку
            pass

        # Отправляем новое сообщение
        await callback_query.message.answer(
            text=text,
            reply_markup=keyboard
        )

def setup_learning_handlers(dp):
    """
    Регистрирует обработчики для центра обучения
    """
    dp.include_router(router)
