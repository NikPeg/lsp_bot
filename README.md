# ЛСП Бот

Телеграм-бот для предоставления студентам вузов учебных материалов (лекции, книги, методички и другие файлы).

## Описание

ЛСП Бот предоставляет доступ к учебным материалам, организованным по факультетам, предметам, типам материалов и семестрам. Интерфейс доступен на трёх языках (русский, английский, арабский).

## Требования

- Python 3.9+
- Telegram Bot API Token

## Установка и настройка

### 1. Клонирование репозитория

```bash
    git clone https://github.com/NikPeg/lsp_bot.git
    cd lsp_bot
```
### 2. Создание виртуального окружения и установка зависимостей
```bash
   bash
   python -m venv venv
   source venv/bin/activate  # На Linux/Mac

# или
    venv\Scripts\activate     # На Windows
    pip install -r requirements.txt
# или с pyenv
    pyenv virtualenv 3.10.12 lsp
    pyenv activate lsp
    pip install -r requirements.txt
```
### 3. Создание необходимых папок
   Следующие папки необходимо создать вручную, так как они не включены в репозиторий:

```bash
# Создание структуры для хранения материалов
mkdir -p data/materials/faculty_L/
mkdir -p data/materials/faculty_S/
mkdir -p data/materials/faculty_P/

# Создание папки для данных пользователей
mkdir -p data/users/

# Создание папки для изображений расписаний
mkdir -p data/images/schedule/
```
### 4. Настройка файла .env
Создайте файл .env в корневой папке проекта со следующим содержимым:
```
# Telegram Bot Token
BOT_TOKEN=ваш_токен_бота

# ID группы администраторов
ADMIN_GROUP_ID=идентификатор_группы_администраторов

# Ссылка на канал
CHANNEL_LINK=https://t.me/your_channel

# Папка с материалами
MATERIALS_FOLDER=data/materials

# Другие настройки
LANGUAGE_DEFAULT=ru
```
### 5. Добавление учебных материалов
   Разместите учебные материалы в соответствующей структуре папок:

```bash
data/materials/
├── faculty_L/
│   ├── subject1/
│   │   ├── lectures/
│   │   │   ├── semester1/
│   │   │   │   ├── lecture1.pdf
│   │   │   │   └── lecture2.pdf
│   │   │   └── semester2/
│   │   ├── books/
│   │   ├── atlases/
│   │   ├── methods/
│   │   ├── exams/
│   │   └── notes/
│   └── subject2/
├── faculty_S/
└── faculty_P/
```
Стукрута папок может быть любой. Расположение папок и файлов являются источником правды в данном боте.
### 6. Добавление изображений расписаний
Поместите изображения с расписаниями в папку data/images/schedule/:
```
data/images/schedule/
├── deanery.jpg
├── sports_doctor.jpg
├── anatomy.jpg
├── libraries.jpg
├── pass_making.jpg
├── practice.jpg
└── departments.jpg
```
### Запуск бота
```bash
  python main.py
```
### Использование
Пользователь начинает взаимодействие, отправляя команду /start  
Выбирает язык интерфейса  
Получает доступ к главному меню с кнопками: Личный кабинет, Центр обучения, Расписание, Наш канал  
В Личном кабинете пользователь выбирает факультет  
В Центре обучения предоставляется доступ к учебным материалам  
Команды для администраторов  
В административной группе доступны следующие команды:  

/users_count - количество уникальных пользователей, запустивших бота  
/active_users - количество активных пользователей за последнюю неделю  
### Структура проекта
Основные компоненты:

`main.py` - точка входа приложения  
`app/` - основной код приложения  
`data/` - хранение данных и материалов  
`materials/` - учебные материалы  
`images/` - изображения расписаний  
`users/` - данные о пользователях  
