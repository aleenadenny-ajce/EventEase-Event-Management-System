import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Load .env file if it exists
load_dotenv(BASE_DIR / ".env")

class Config:
    """Application configuration loaded from environment variables with safe defaults."""
    APP_NAME = os.getenv("APP_NAME", "EventEase")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    
    # Secret Key for session management and CSRF protection
    SECRET_KEY = os.getenv("SECRET_KEY", "eventease-dev-insecure-secret-key-replace-in-production-2026")
    
    # Database configuration
    DB_PATH_ENV = os.getenv("DATABASE_PATH", "database/eventease.db")
    if os.path.isabs(DB_PATH_ENV):
        DATABASE = Path(DB_PATH_ENV)
    else:
        DATABASE = BASE_DIR / DB_PATH_ENV
        
    DEBUG = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    TESTING = False
    
    # Upload folder for posters
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max file upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    
    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class TestConfig(Config):
    """Configuration for automated test execution."""
    TESTING = True
    DEBUG = False
    SECRET_KEY = "test-secret-key-not-for-production"
    # Tests use a dedicated temporary/in-memory or test database
    DATABASE = BASE_DIR / "database" / "test_eventease.db"
