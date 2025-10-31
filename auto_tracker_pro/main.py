#!/usr/bin/env python3
"""
Auto Tracker Pro - Main Entry Point
Система відстеження транспортних засобів
"""

import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.app import EnhancedAutoTrackerApp

def main():
    """Главная функция запуска приложения"""
    try:
        app = EnhancedAutoTrackerApp()
        app.mainloop()
    except Exception as e:
        print(f"Помилка запуску програми: {e}")
        input("Натисніть Enter для виходу...")

if __name__ == "__main__":
    main()