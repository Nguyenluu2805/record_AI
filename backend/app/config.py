import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    COMPANY_NAME: str = "CÔNG TY CỔ PHẦN TẬP ĐOÀN KIM LONG PHÁT"
    COMPANY_SHORT: str = "KIM LONG PHÁT GROUP"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("PORT", os.getenv("SERVER_PORT", "8000")))
    
    # Audio config
    INPUT_SAMPLE_RATE: int = 16000
    
    # Directories
    BACKEND_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BASE_DIR: str = os.path.dirname(BACKEND_DIR)
    FRONTEND_DIR: str = os.path.join(BASE_DIR, "frontend")
    OUTPUT_DIR: str = os.path.join(BASE_DIR, "output")
    RECORDINGS_DIR: str = os.path.join(OUTPUT_DIR, "recordings")
    TRANSCRIPTS_DIR: str = os.path.join(OUTPUT_DIR, "transcripts")

settings = Settings()
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.RECORDINGS_DIR, exist_ok=True)
os.makedirs(settings.TRANSCRIPTS_DIR, exist_ok=True)
