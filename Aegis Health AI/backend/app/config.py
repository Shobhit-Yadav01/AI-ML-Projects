import os
from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENV_FILE = os.path.join(_BASE_DIR, ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Medical Intelligence Platform"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("JWT_SECRET", "super_secret_healthcare_key_12984710")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # AI Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Vector DB
    VECTOR_DB_MODE: str = "numpy"  # "numpy" or "chroma"
    DATA_DIR: str = os.path.join(_BASE_DIR, "data")
    MODEL_DIR: str = os.path.join(_BASE_DIR, "model")
    MODEL_PATH: str = os.path.join(_BASE_DIR, "tumor_detection_model.h5")

    model_config = SettingsConfigDict(case_sensitive=True, env_file=_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

settings = Settings()

