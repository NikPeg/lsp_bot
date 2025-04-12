import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from loguru import logger

@dataclass
class Faculty:
    id: str
    name: str
    path: Path

@dataclass
class Subject:
    id: str
    name: str
    path: Path

@dataclass
class MaterialFile:
    id: str
    name: str
    path: Path
    size: int

class FileManager:
    def __init__(self, base_path: Path = Path("data/materials")):
        self.base_path = base_path
        self.faculty_names = {
            "faculty_L": "Лингвистический",
            "faculty_S": "Социальных наук",
            "faculty_P": "Прикладных наук"
        }
        self.material_types = {
            "lectures": "Лекции",
            "books": "Книги",
            "atlases": "Атласы",
            "methods": "Методички",
            "exams": "Экзамены",
            "notes": "Шпаргалки"
        }

    async def get_faculties(self) -> List[Faculty]:
        """Получает список всех факультетов"""
        faculties = []
        try:
            for dir_name in os.listdir(self.base_path):
                if dir_name.startswith("faculty_"):
                    faculty_id = dir_name.split("_")[1].lower()
                    faculties.append(
                        Faculty(
                            id=faculty_id,
                            name=self.faculty_names.get(dir_name, dir_name),
                            path=self.base_path / dir_name
                        )
                    )
            return sorted(faculties, key=lambda x: x.name)
        except Exception as e:
            logger.error(f"Error getting faculties: {e}")
            return []

    async def get_subjects(self, faculty_id: str) -> List[Subject]:
        """Получает список предметов для факультета"""
        subjects = []
        faculty_dir = self.base_path / f"faculty_{faculty_id.upper()}"

        try:
            if faculty_dir.exists():
                for dir_name in os.listdir(faculty_dir):
                    subject_path = faculty_dir / dir_name
                    if subject_path.is_dir():
                        subjects.append(
                            Subject(
                                id=dir_name.lower(),
                                name=dir_name.replace("_", " ").title(),
                                path=subject_path
                            )
                        )
            return sorted(subjects, key=lambda x: x.name)
        except Exception as e:
            logger.error(f"Error getting subjects for faculty {faculty_id}: {e}")
            return []

    async def get_semesters(
            self,
            faculty_id: str,
            subject_id: str,
            material_type: str
    ) -> List[str]:
        """Получает список семестров для материала"""
        semesters = []
        material_path = (
                self.base_path /
                f"faculty_{faculty_id.upper()}" /
                subject_id /
                material_type
        )

        try:
            if material_path.exists():
                for dir_name in os.listdir(material_path):
                    if dir_name.startswith("semester"):
                        semesters.append(dir_name.split("_")[1])
                return sorted(semesters)
            return []
        except Exception as e:
            logger.error(f"Error getting semesters: {e}")
            return []

    async def get_files(
            self,
            faculty_id: str,
            subject_id: str,
            material_type: str,
            semester: str
    ) -> List[MaterialFile]:
        """Получает список файлов для семестра"""
        files = []
        semester_path = (
                self.base_path /
                f"faculty_{faculty_id.upper()}" /
                subject_id /
                material_type /
                f"semester_{semester}"
        )

        try:
            if semester_path.exists():
                for file_name in os.listdir(semester_path):
                    file_path = semester_path / file_name
                    if file_path.is_file():
                        files.append(
                            MaterialFile(
                                id=file_name.lower(),
                                name=os.path.splitext(file_name)[0],
                                path=file_path,
                                size=file_path.stat().st_size
                            )
                        )
            return sorted(files, key=lambda x: x.name)
        except Exception as e:
            logger.error(f"Error getting files: {e}")
            return []

    async def get_file_path(
            self,
            faculty_id: str,
            subject_id: str,
            material_type: str,
            semester: str,
            file_id: str
    ) -> Optional[Path]:
        """Получает полный путь к файлу"""
        file_path = (
                self.base_path /
                f"faculty_{faculty_id.upper()}" /
                subject_id /
                material_type /
                f"semester_{semester}" /
                file_id
        )
        return file_path if file_path.exists() else None

    async def check_file_exists(self, file_path: Path) -> bool:
        """Проверяет существование файла"""
        return file_path.exists()

    async def get_material_type_name(self, material_type: str) -> str:
        """Получает человекочитаемое название типа материала"""
        return self.material_types.get(material_type, material_type)
