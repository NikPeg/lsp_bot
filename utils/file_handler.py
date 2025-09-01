import os
import zipfile
import tempfile
import asyncio
from typing import Optional, List, Tuple
from aiogram.types import FSInputFile, Message, CallbackQuery
from aiogram import Bot

# Лимиты Telegram API (в байтах)
TELEGRAM_FILE_SIZE_LIMIT = 50 * 1024 * 1024  # 50 МБ
TELEGRAM_PHOTO_SIZE_LIMIT = 10 * 1024 * 1024  # 10 МБ

class FileSizeError(Exception):
    """Исключение для файлов, превышающих лимиты"""
    pass

async def get_file_size(file_path: str) -> int:
    """
    Получает размер файла в байтах
    
    Args:
        file_path (str): Путь к файлу
        
    Returns:
        int: Размер файла в байтах
    """
    try:
        return await asyncio.to_thread(os.path.getsize, file_path)
    except Exception:
        return 0

def format_file_size(size_bytes: int) -> str:
    """
    Форматирует размер файла для отображения
    
    Args:
        size_bytes (int): Размер в байтах
        
    Returns:
        str: Отформатированный размер
    """
    if size_bytes < 1024:
        return f"{size_bytes} Б"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} КБ"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} МБ"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} ГБ"

async def check_file_size_limits(file_path: str, is_photo: bool = False) -> Tuple[bool, str]:
    """
    Проверяет, не превышает ли файл лимиты Telegram
    
    Args:
        file_path (str): Путь к файлу
        is_photo (bool): Является ли файл фотографией
        
    Returns:
        Tuple[bool, str]: (можно_отправить, сообщение_об_ошибке)
    """
    file_size = await get_file_size(file_path)
    limit = TELEGRAM_PHOTO_SIZE_LIMIT if is_photo else TELEGRAM_FILE_SIZE_LIMIT
    
    if file_size > limit:
        limit_str = format_file_size(limit)
        size_str = format_file_size(file_size)
        return False, f"Файл слишком большой ({size_str}). Максимальный размер: {limit_str}"
    
    return True, ""

async def create_compressed_archive(file_path: str, compression_level: int = 6) -> Optional[str]:
    """
    Создает сжатый архив файла
    
    Args:
        file_path (str): Путь к исходному файлу
        compression_level (int): Уровень сжатия (0-9)
        
    Returns:
        Optional[str]: Путь к созданному архиву или None при ошибке
    """
    try:
        # Создаем временный файл для архива
        temp_dir = tempfile.gettempdir()
        file_name = os.path.basename(file_path)
        archive_name = f"{os.path.splitext(file_name)[0]}.zip"
        archive_path = os.path.join(temp_dir, f"compressed_{archive_name}")
        
        def create_zip():
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
                zipf.write(file_path, file_name)
        
        await asyncio.to_thread(create_zip)
        return archive_path
        
    except Exception as e:
        print(f"Ошибка создания архива: {e}")
        return None

async def split_file(file_path: str, chunk_size: int = 45 * 1024 * 1024) -> List[str]:
    """
    Разбивает файл на части
    
    Args:
        file_path (str): Путь к исходному файлу
        chunk_size (int): Размер части в байтах (по умолчанию 45 МБ)
        
    Returns:
        List[str]: Список путей к частям файла
    """
    try:
        temp_dir = tempfile.gettempdir()
        file_name = os.path.basename(file_path)
        base_name = os.path.splitext(file_name)[0]
        extension = os.path.splitext(file_name)[1]
        
        parts = []
        
        def split_file_sync():
            with open(file_path, 'rb') as source_file:
                part_num = 1
                while True:
                    chunk = source_file.read(chunk_size)
                    if not chunk:
                        break
                    
                    part_name = f"{base_name}.part{part_num:03d}{extension}"
                    part_path = os.path.join(temp_dir, part_name)
                    
                    with open(part_path, 'wb') as part_file:
                        part_file.write(chunk)
                    
                    parts.append(part_path)
                    part_num += 1
        
        await asyncio.to_thread(split_file_sync)
        return parts
        
    except Exception as e:
        print(f"Ошибка разбивки файла: {e}")
        return []

async def send_large_file(bot: Bot, chat_id: int, file_path: str, caption: str = "", 
                         is_photo: bool = False) -> Tuple[bool, str]:
    """
    Отправляет большой файл, применяя различные стратегии
    
    Args:
        bot (Bot): Экземпляр бота
        chat_id (int): ID чата
        file_path (str): Путь к файлу
        caption (str): Подпись к файлу
        is_photo (bool): Является ли файл фотографией
        
    Returns:
        Tuple[bool, str]: (успешно_отправлено, сообщение)
    """
    # Проверяем размер файла
    can_send, error_msg = await check_file_size_limits(file_path, is_photo)
    
    if can_send:
        # Файл можно отправить как есть
        try:
            file = FSInputFile(file_path)
            if is_photo:
                await bot.send_photo(chat_id, photo=file, caption=caption)
            else:
                await bot.send_document(chat_id, document=file, caption=caption)
            return True, "Файл успешно отправлен"
        except Exception as e:
            return False, f"Ошибка при отправке файла: {str(e)}"
    
    # Файл слишком большой, пробуем сжать
    file_size = await get_file_size(file_path)
    await bot.send_message(chat_id, f"📦 Файл большой ({format_file_size(file_size)}). Создаю сжатый архив...")
    
    compressed_path = await create_compressed_archive(file_path)
    if compressed_path:
        # Проверяем размер сжатого файла
        can_send_compressed, _ = await check_file_size_limits(compressed_path, False)
        
        if can_send_compressed:
            try:
                compressed_file = FSInputFile(compressed_path)
                compressed_size = await get_file_size(compressed_path)
                new_caption = f"📦 Сжатый архив ({format_file_size(compressed_size)})\n{caption}"
                
                await bot.send_document(chat_id, document=compressed_file, caption=new_caption)
                
                # Удаляем временный файл
                await asyncio.to_thread(os.remove, compressed_path)
                return True, "Файл отправлен в виде сжатого архива"
            except Exception as e:
                await asyncio.to_thread(os.remove, compressed_path)
                return False, f"Ошибка при отправке сжатого файла: {str(e)}"
    
    # Сжатие не помогло, разбиваем на части
    await bot.send_message(chat_id, "📂 Разбиваю файл на части...")
    
    parts = await split_file(file_path)
    if not parts:
        return False, "Не удалось разбить файл на части"
    
    try:
        # Отправляем информацию о частях
        parts_info = f"📂 Файл разбит на {len(parts)} частей:\n"
        for i, part_path in enumerate(parts, 1):
            part_size = await get_file_size(part_path)
            parts_info += f"Часть {i}: {format_file_size(part_size)}\n"
        
        await bot.send_message(chat_id, parts_info)
        
        # Отправляем каждую часть
        for i, part_path in enumerate(parts, 1):
            part_file = FSInputFile(part_path)
            part_caption = f"Часть {i}/{len(parts)}: {os.path.basename(part_path)}"
            
            await bot.send_document(chat_id, document=part_file, caption=part_caption)
            
            # Удаляем временный файл части
            await asyncio.to_thread(os.remove, part_path)
        
        return True, f"Файл отправлен в {len(parts)} частях"
        
    except Exception as e:
        # Очищаем временные файлы при ошибке
        for part_path in parts:
            try:
                await asyncio.to_thread(os.remove, part_path)
            except:
                pass
        return False, f"Ошибка при отправке частей файла: {str(e)}"

def cleanup_temp_files():
    """
    Очищает временные файлы (можно вызывать периодически)
    """
    try:
        temp_dir = tempfile.gettempdir()
        for filename in os.listdir(temp_dir):
            if filename.startswith(('compressed_', 'part')):
                file_path = os.path.join(temp_dir, filename)
                try:
                    os.remove(file_path)
                except:
                    pass
    except:
        pass