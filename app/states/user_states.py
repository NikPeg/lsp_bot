from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    """Состояния пользователя для FSM"""
    # Состояния выбора языка
    selecting_language = State()

    # Состояния личного кабинета
    selecting_faculty = State()
    changing_faculty = State()

    # Состояния центра обучения
    selecting_subject = State()
    selecting_material_type = State()
    selecting_semester = State()
    viewing_materials = State()

    # Состояния расписания
    viewing_schedule = State()
    selecting_schedule_type = State()

    # Состояния администратора
    admin_actions = State()
    viewing_statistics = State()


class FacultyData:
    """Класс для хранения данных о факультете"""
    def __init__(self):
        self.current_faculty = None


class LearningData:
    """Класс для хранения данных о процессе обучения"""
    def __init__(self):
        self.current_subject = None
        self.current_material_type = None
        self.current_semester = None
        self.current_file = None


class ScheduleData:
    """Класс для хранения данных о расписании"""
    def __init__(self):
        self.current_schedule_type = None


class UserData:
    """Основной класс для хранения данных пользователя"""
    def __init__(self):
        self.language = 'ru'
        self.faculty_data = FacultyData()
        self.learning_data = LearningData()
        self.schedule_data = ScheduleData()
        self.is_admin = False
