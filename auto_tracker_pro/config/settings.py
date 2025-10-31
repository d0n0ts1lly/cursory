import os
from pathlib import Path

class Config:
    """Конфигурация приложения"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    ASSETS_DIR = BASE_DIR / "assets"
    USER_AVATARS = ASSETS_DIR / "avatars"
    
    # Database configuration
    DB_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "23032023",
        "database": "shipping_db",
        "port": 3306,
    }
    
    # UI Settings
    CANVAS_WIDTH = 900
    CANVAS_HEIGHT = 420
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 800
    MIN_WINDOW_WIDTH = 1200
    MIN_WINDOW_HEIGHT = 700
    
    # Theme
    DEFAULT_THEME = "minty"
    DARK_THEME = "darkly"
    
    # File paths
    MAP_PATH = ASSETS_DIR / "map_region.png"
    DEFAULT_CAR = ASSETS_DIR / "default_car.png"
    
    @classmethod
    def create_directories(cls):
        """Создает необходимые директории"""
        cls.ASSETS_DIR.mkdir(exist_ok=True)
        cls.USER_AVATARS.mkdir(exist_ok=True)
    
    @classmethod
    def get_user_avatar_path(cls, user_id):
        """Возвращает путь к аватару пользователя"""
        return cls.USER_AVATARS / f"user_{user_id}.png"

# Создаем директории при импорте
Config.create_directories()