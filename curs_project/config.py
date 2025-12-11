import os

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "23032023",
    "database": "shipping_db",
    "port": 3306,
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 450

MAP_COORDINATES = {
}