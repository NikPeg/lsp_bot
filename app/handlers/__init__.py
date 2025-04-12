"""
Инициализация и объединение всех роутеров обработчиков.
"""

from aiogram import Router

from app.handlers.admin import admin_router
from app.handlers.start import start_router
from app.handlers.main_menu import main_menu_router
from app.handlers.profile import profile_router
from app.handlers.learning_center import learning_center_router
from app.handlers.faculty import faculty_router
from app.handlers.materials import materials_router
from app.handlers.schedule import schedule_router
from app.handlers.channel import channel_router

# Создаем общий роутер для всех обработчиков
router = Router()

# Подключаем все роутеры обработчиков к основному роутеру
router.include_router(admin_router)
router.include_router(start_router)
router.include_router(main_menu_router)
router.include_router(profile_router)
router.include_router(learning_center_router)
router.include_router(faculty_router)
router.include_router(materials_router)
router.include_router(schedule_router)
router.include_router(channel_router)

# Экспортируем общий роутер
__all__ = ["router"]
