import os
import zipfile
import tempfile
import asyncio
from typing import Optional, List, Tuple
from aiogram.types import FSInputFile, Message, CallbackQuery
from aiogram import Bot
from services.text_manager import get_text

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

async def create_multipart_archives(file_path: str, max_archive_size: int = 45 * 1024 * 1024) -> List[str]:
    """
    Создает многотомный ZIP архив из файла
    
    Args:
        file_path (str): Путь к исходному файлу
        max_archive_size (int): Максимальный размер одного архива в байтах
        
    Returns:
        List[str]: Список путей к архивам
    """
    try:
        temp_dir = tempfile.gettempdir()
        file_name = os.path.basename(file_path)
        base_name = os.path.splitext(file_name)[0]
        
        archives = []
        
        def create_archives_sync():
            file_size = os.path.getsize(file_path)
            
            # Если файл помещается в один архив
            if file_size <= max_archive_size * 0.9:  # 90% от лимита для запаса
                archive_path = os.path.join(temp_dir, f"{base_name}.zip")
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                    zipf.write(file_path, file_name)
                archives.append(archive_path)
                return
            
            # Создаем многотомный архив
            # Читаем файл частями и создаем отдельные архивы
            chunk_size = int(max_archive_size * 0.8)  # 80% от лимита для сжатия
            
            with open(file_path, 'rb') as source_file:
                part_num = 1
                while True:
                    chunk = source_file.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Создаем временный файл для части
                    temp_part_path = os.path.join(temp_dir, f"temp_part_{part_num}.dat")
                    with open(temp_part_path, 'wb') as temp_part:
                        temp_part.write(chunk)
                    
                    # Создаем архив для этой части
                    archive_name = f"{base_name}_part{part_num:02d}.zip"
                    archive_path = os.path.join(temp_dir, archive_name)
                    
                    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                        zipf.write(temp_part_path, f"{base_name}_part{part_num:02d}.dat")
                    
                    archives.append(archive_path)
                    
                    # Удаляем временный файл части
                    os.remove(temp_part_path)
                    part_num += 1
        
        await asyncio.to_thread(create_archives_sync)
        return archives
        
    except Exception as e:
        print(f"Ошибка создания многотомного архива: {e}")
        return []

def get_multipart_instructions(language: str, parts_count: int) -> str:
    """
    Получает локализованную инструкцию по распаковке многотомного архива
    
    Args:
        language (str): Код языка
        parts_count (int): Количество частей архива
        
    Returns:
        str: Инструкция на нужном языке
    """
    if language == "en":
        instruction = f"\n📋 File recovery instructions:\n"
        instruction += f"1️⃣ Download all {parts_count} volumes\n"
        instruction += f"2️⃣ Extract .dat files from each archive\n"
        instruction += f"3️⃣ Combine parts in correct order:\n"
        instruction += f"   • Windows: copy /b part01.dat + part02.dat + ... file.pdf\n"
        instruction += f"   • Linux/Mac: cat part01.dat part02.dat ... > file.pdf"
    elif language == "ar":
        instruction = f"\n📋 تعليمات استعادة الملف:\n"
        instruction += f"1️⃣ قم بتنزيل جميع الأجزاء الـ {parts_count}\n"
        instruction += f"2️⃣ استخرج ملفات .dat من كل أرشيف\n"
        instruction += f"3️⃣ ادمج الأجزاء بالترتيب الصحيح:\n"
        instruction += f"   • Windows: copy /b part01.dat + part02.dat + ... file.pdf\n"
        instruction += f"   • Linux/Mac: cat part01.dat part02.dat ... > file.pdf"
    else:  # ru
        instruction = f"\n📋 Инструкция по восстановлению файла:\n"
        instruction += f"1️⃣ Скачайте все {parts_count} томов\n"
        instruction += f"2️⃣ Извлеките .dat файлы из каждого архива\n"
        instruction += f"3️⃣ Объедините части в правильном порядке:\n"
        instruction += f"   • Windows: copy /b part01.dat + part02.dat + ... file.pdf\n"
        instruction += f"   • Linux/Mac: cat part01.dat part02.dat ... > file.pdf"
    
    return instruction

async def send_large_file(bot: Bot, chat_id: int, file_path: str, caption: str = "",
                         is_photo: bool = False, language: str = "ru") -> Tuple[bool, str]:
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
    
    # Сжатие не помогло, создаем многотомный архив
    await bot.send_message(chat_id, "📂 Создаю многотомный архив...")
    
    archives = await create_multipart_archives(file_path)
    if not archives:
        return False, "Не удалось создать многотомный архив"
    
    try:
        # Отправляем информацию об архивах
        if len(archives) == 1:
            archive_size = await get_file_size(archives[0])
            info_text = f"📦 Создан сжатый архив ({format_file_size(archive_size)})"
        else:
            info_text = f"📂 Создан многотомный архив из {len(archives)} частей:\n"
            for i, archive_path in enumerate(archives, 1):
                archive_size = await get_file_size(archive_path)
                info_text += f"Том {i}: {format_file_size(archive_size)}\n"
            
            # Добавляем локализованную инструкцию по распаковке
            info_text += get_multipart_instructions(language, len(archives))
        
        await bot.send_message(chat_id, info_text)
        
        # Отправляем каждый архив
        for i, archive_path in enumerate(archives, 1):
            archive_file = FSInputFile(archive_path)
            if len(archives) == 1:
                archive_caption = f"📦 {os.path.basename(archive_path)}"
            else:
                archive_caption = f"📂 Том {i}/{len(archives)}: {os.path.basename(archive_path)}"
            
            await bot.send_document(chat_id, document=archive_file, caption=archive_caption)
            
            # Удаляем временный архив
            await asyncio.to_thread(os.remove, archive_path)
        
        if len(archives) == 1:
            return True, "Файл отправлен в виде сжатого архива"
        else:
            return True, f"Файл отправлен многотомным архивом ({len(archives)} томов)"
        
    except Exception as e:
        # Очищаем временные файлы при ошибке
        for archive_path in archives:
            try:
                await asyncio.to_thread(os.remove, archive_path)
            except:
                pass
        return False, f"Ошибка при отправке архивов: {str(e)}"

def cleanup_temp_files():
    """
    Очищает временные файлы (можно вызывать периодически)
    """
    try:
        temp_dir = tempfile.gettempdir()
        for filename in os.listdir(temp_dir):
            if filename.startswith(('compressed_', 'part', 'temp_part_')) or '_part' in filename and filename.endswith('.zip'):
                file_path = os.path.join(temp_dir, filename)
                try:
                    os.remove(file_path)
                except:
                    pass
    except:
        pass