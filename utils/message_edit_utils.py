import hashlib
from typing import Optional, Union
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
import logging

logger = logging.getLogger(__name__)

def get_content_hash(text: str, reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = None) -> str:
    """
    Создает хэш контента сообщения для проверки изменений
    
    Args:
        text (str): Текст сообщения
        reply_markup: Клавиатура сообщения
        
    Returns:
        str: MD5 хэш контента
    """
    content = text
    if reply_markup:
        # Добавляем информацию о клавиатуре в хэш
        if hasattr(reply_markup, 'inline_keyboard'):
            # Для InlineKeyboardMarkup
            keyboard_data = str(reply_markup.inline_keyboard)
        elif hasattr(reply_markup, 'keyboard'):
            # Для ReplyKeyboardMarkup
            keyboard_data = str(reply_markup.keyboard)
        else:
            keyboard_data = str(reply_markup)
        content += keyboard_data
    
    return hashlib.md5(content.encode('utf-8')).hexdigest()

# Глобальный кэш для хранения хэшей сообщений
_message_content_cache = {}

def get_message_cache_key(chat_id: int, message_id: int) -> str:
    """Создает ключ для кэша сообщений"""
    return f"{chat_id}:{message_id}"

def cache_message_content(chat_id: int, message_id: int, text: str, 
                         reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = None):
    """
    Кэширует контент сообщения
    
    Args:
        chat_id (int): ID чата
        message_id (int): ID сообщения
        text (str): Текст сообщения
        reply_markup: Клавиатура сообщения
    """
    cache_key = get_message_cache_key(chat_id, message_id)
    content_hash = get_content_hash(text, reply_markup)
    _message_content_cache[cache_key] = content_hash

def is_content_changed(chat_id: int, message_id: int, new_text: str,
                      new_reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = None) -> bool:
    """
    Проверяет, изменился ли контент сообщения
    
    Args:
        chat_id (int): ID чата
        message_id (int): ID сообщения
        new_text (str): Новый текст
        new_reply_markup: Новая клавиатура
        
    Returns:
        bool: True если контент изменился, False если нет
    """
    cache_key = get_message_cache_key(chat_id, message_id)
    old_hash = _message_content_cache.get(cache_key)
    
    if old_hash is None:
        # Если нет кэшированного контента, считаем что изменился
        return True
    
    new_hash = get_content_hash(new_text, new_reply_markup)
    return old_hash != new_hash

async def safe_edit_caption(callback_query: CallbackQuery, caption: str,
                           reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = None) -> bool:
    """
    Безопасно редактирует подпись к сообщению с проверкой изменений
    
    Args:
        callback_query (CallbackQuery): Callback query объект
        caption (str): Новая подпись
        reply_markup: Новая клавиатура
        
    Returns:
        bool: True если сообщение было отредактировано, False если нет изменений
    """
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    
    # Проверяем, изменился ли контент
    if not is_content_changed(chat_id, message_id, caption, reply_markup):
        logger.debug(f"Content not changed for message {message_id}, skipping edit")
        return False
    
    try:
        await callback_query.message.edit_caption(
            caption=caption,
            reply_markup=reply_markup
        )
        
        # Кэшируем новый контент
        cache_message_content(chat_id, message_id, caption, reply_markup)
        logger.debug(f"Successfully edited caption for message {message_id}")
        return True
        
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logger.debug(f"Message {message_id} is not modified, caching current content")
            # Кэшируем текущий контент, чтобы избежать повторных попыток
            cache_message_content(chat_id, message_id, caption, reply_markup)
            return False
        elif "message to edit not found" in str(e):
            logger.warning(f"Message {message_id} not found for editing")
            return False
        else:
            logger.error(f"Error editing caption for message {message_id}: {e}")
            raise

async def safe_edit_text(callback_query: CallbackQuery, text: str,
                        reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = None) -> bool:
    """
    Безопасно редактирует текст сообщения с проверкой изменений
    
    Args:
        callback_query (CallbackQuery): Callback query объект
        text (str): Новый текст
        reply_markup: Новая клавиатура
        
    Returns:
        bool: True если сообщение было отредактировано, False если нет изменений
    """
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    
    # Проверяем, изменился ли контент
    if not is_content_changed(chat_id, message_id, text, reply_markup):
        logger.debug(f"Content not changed for message {message_id}, skipping edit")
        return False
    
    try:
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )
        
        # Кэшируем новый контент
        cache_message_content(chat_id, message_id, text, reply_markup)
        logger.debug(f"Successfully edited text for message {message_id}")
        return True
        
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logger.debug(f"Message {message_id} is not modified, caching current content")
            # Кэшируем текущий контент, чтобы избежать повторных попыток
            cache_message_content(chat_id, message_id, text, reply_markup)
            return False
        elif "message to edit not found" in str(e):
            logger.warning(f"Message {message_id} not found for editing")
            return False
        else:
            logger.error(f"Error editing text for message {message_id}: {e}")
            raise

def clear_message_cache():
    """Очищает кэш сообщений (можно вызывать периодически)"""
    global _message_content_cache
    _message_content_cache.clear()
    logger.debug("Message content cache cleared")