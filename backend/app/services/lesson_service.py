import os
import json
from typing import Dict, Any, List

# Đường dẫn tới thư mục data/sample_lessons ở thư mục gốc của project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(ROOT_DIR, "data", "sample_lessons")
if not os.path.exists(DATA_DIR):
    DATA_DIR = os.path.join(os.path.dirname(ROOT_DIR), "data", "sample_lessons")

class LessonService:
    @staticmethod
    def list_lessons() -> List[Dict[str, str]]:
        lessons = []
        if not os.path.exists(DATA_DIR):
            return lessons
        for fname in os.listdir(DATA_DIR):
            if fname.endswith(".json"):
                fpath = os.path.join(DATA_DIR, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        lessons.append({
                            "id": data.get("lesson_id", fname.replace(".json", "")),
                            "title": data.get("title", "Bài học"),
                            "subject": data.get("subject", ""),
                            "filename": fname
                        })
                except Exception as e:
                    print(f"Lỗi đọc file lesson {fname}: {e}")
        return lessons

    @staticmethod
    def get_lesson(lesson_id: str) -> Dict[str, Any] | None:
        if not os.path.exists(DATA_DIR):
            return None
        for fname in os.listdir(DATA_DIR):
            if fname.endswith(".json"):
                fpath = os.path.join(DATA_DIR, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("lesson_id") == lesson_id or fname.replace(".json", "") == lesson_id:
                            return data
                except Exception:
                    pass
        return None

lesson_service = LessonService()
