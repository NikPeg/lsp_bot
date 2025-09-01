import os
from dotenv import load_dotenv
from pathlib import Path

# Загрузка переменных окружения из .env файла
load_dotenv()

# Основные настройки бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")
MATERIALS_FOLDER = os.getenv("MATERIALS_FOLDER", "data/materials")
IMAGES_FOLDER = os.getenv("IMAGES_FOLDER", "images/schedule")
INTERFACE_IMAGES_FOLDER = os.getenv("INTERFACE_IMAGES_FOLDER", "images/interface")
DEFAULT_LANGUAGE = os.getenv("LANGUAGE_DEFAULT", "ru")

# Пути к директориям проекта
BASE_DIR = Path(__file__).resolve().parent
TEXTS_DIR = BASE_DIR / "texts"
DATABASE_PATH = BASE_DIR / "database" / "lsp_bot.db"

# Инструкции для личного кабинета
PROFILE_INSTRUCTIONS = {
    "ru": """🎓 Добро пожаловать в Личный кабинет!

Этот бот предоставляет доступ к учебным материалам для студентов. 

Как пользоваться:
1. Выберите ваш факультет ниже
2. В Центре обучения вы найдете материалы вашего факультета
3. В разделе Расписание доступны графики работы различных подразделений
4. Подпишитесь на наш канал для получения важных обновлений

Приятного использования!""",

    "en": """🎓 Welcome to your Profile!

This bot provides access to educational materials for students.

How to use:
1. Select your faculty below
2. In the Learning Center you'll find materials for your faculty
3. The Schedule section contains working hours for various departments
4. Subscribe to our channel for important updates

Enjoy using the bot!""",

    "ar": """🎓 مرحبًا بك في حسابك الشخصي!

يوفر هذا الروبوت إمكانية الوصول إلى المواد التعليمية للطلاب.

كيفية الاستخدام:
1. اختر كليتك أدناه
2. في مركز التعلم ستجد مواد لكليتك
3. يحتوي قسم الجدول الزمني على ساعات العمل لمختلف الأقسام
4. اشترك في قناتنا للحصول على التحديثات المهمة

استمتع باستخدام الروبوت!"""
}

# Сообщение при отсутствии понимания команды
UNKNOWN_COMMAND = {
    "ru": "🤔 Я не понимаю эту команду. Пожалуйста, используйте кнопки для навигации.",
    "en": "🤔 I don't understand this command. Please use the buttons for navigation.",
    "ar": "🤔 أنا لا أفهم هذا الأمر. يرجى استخدام الأزرار للتنقل."
}
