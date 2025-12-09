import os

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "23032023",
    "database": "shipping_db",
    "port": 3306,
}

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Canvas target size
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 450

# Map coordinates (pixels on canvas)
MAP_COORDINATES = {
}