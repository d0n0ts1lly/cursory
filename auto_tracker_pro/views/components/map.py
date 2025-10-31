import os
from PIL import Image, ImageTk
from tkinter import Canvas
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from config.settings import Config
from mysql.connector import Error

class MapManager:
    """Менеджер для работы с картой"""
    
    def __init__(self, parent, connection):
        self.parent = parent
        self.conn = connection
        self.map_canvas = None
        self.map_image = None
        self.map_tk = None
    
    def create_map_canvas(self, parent):
        """Создание canvas для карты"""
        if not os.path.exists(Config.MAP_PATH):
            # Создаем placeholder карту
            self.map_canvas = Canvas(parent, width=Config.CANVAS_WIDTH, 
                                   height=Config.CANVAS_HEIGHT, 
                                   bg="#e9f7ef", highlightthickness=1, 
                                   highlightbackground="#ccc")
            self.map_canvas.pack(fill="both", expand=True)
            
            self._draw_simple_map()
            self.map_image = None
            
            # Инструкция по добавлению карты
            self.map_canvas.create_text(
                Config.CANVAS_WIDTH//2, Config.CANVAS_HEIGHT//2, 
                text="Для відображення карти:\n1. Знайдіть карту світу у PNG форматі\n2. Збережіть її як 'map_region.png'\n3. Розмістіть у папці 'assets'", 
                font=("Segoe UI", 12), fill="#666", justify="center"
            )
        else:
            # Загружаем реальную карту
            img = Image.open(Config.MAP_PATH)
            w, h = img.size
            ratio = min(Config.CANVAS_WIDTH / w, Config.CANVAS_HEIGHT / h)
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            self.map_image = img
            self.map_tk = ImageTk.PhotoImage(img)
            
            self.map_canvas = Canvas(parent, width=new_w, height=new_h, 
                                   bg="white", highlightthickness=1, 
                                   highlightbackground="#ccc")
            self.map_canvas.create_image(0, 0, anchor="nw", image=self.map_tk)
            self.map_canvas.pack(fill="both", expand=True)
            
            # Добавляем точки маршрута
            self._draw_route_points()
        
        return self.map_canvas
    
    def _draw_simple_map(self):
        """Рисует простую карту если нет файла"""
        canvas = self.map_canvas
        
        # Фон
        canvas.create_rectangle(0, 0, Config.CANVAS_WIDTH, Config.CANVAS_HEIGHT, 
                              fill="#e9f7ef", outline="")
        
        # Континенты (упрощенные)
        continents = [
            # Северная Америка
            (100, 100, 300, 300, "#4CAF50", "Північна Америка"),
            # Европа
            (400, 150, 500, 250, "#2196F3", "Європа"),
            # Азия
            (500, 100, 700, 300, "#FF9800", "Азія"),
        ]
        
        for x1, y1, x2, y2, color, name in continents:
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#333", width=2)
            canvas.create_text((x1+x2)//2, (y1+y2)//2, text=name, 
                             font=("Segoe UI", 10, "bold"))
    
    def _draw_route_points(self):
        """Рисует точки маршрута на карте"""
        if not self.map_canvas:
            return
            
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute("""
                SELECT name, latitude, longitude, transport_mode, status_id
                FROM delivery_route_points 
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                LIMIT 20
            """)
            points = cur.fetchall()
            cur.close()
            
            for point in points:
                self._draw_point_on_map(point)
                
        except Error as e:
            print(f"Error loading route points: {e}")
    
    def _draw_point_on_map(self, point):
        """Рисует одну точку на карте"""
        lat = point.get('latitude', 0)
        lon = point.get('longitude', 0)
        name = point.get('name', '')
        transport = point.get('transport_mode', '')
        
        # Простая проекция координат на canvas
        x = (lon + 180) * (Config.CANVAS_WIDTH / 360)
        y = (90 - lat) * (Config.CANVAS_HEIGHT / 180)
        
        # Цвет в зависимости от транспорта
        colors = {
            'морем': '#2196F3',
            'поезд': '#4CAF50', 
            'грузовик': '#FF9800'
        }
        color = colors.get(transport, '#9C27B0')
        
        # Рисуем точку
        self.map_canvas.create_oval(x-5, y-5, x+5, y+5, fill=color, outline="#333", width=2)
        
        # Подпись
        self.map_canvas.create_text(x, y-15, text=name, font=("Segoe UI", 8, "bold"),
                                  fill="#333", anchor="s")
    
    def draw_car_route(self, purchase_id):
        """Рисует маршрут для конкретного автомобиля"""
        if not self.map_canvas:
            return
            
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute("""
                SELECT name, latitude, longitude, transport_mode, status_id
                FROM delivery_route_points 
                WHERE purchase_id = %s AND latitude IS NOT NULL AND longitude IS NOT NULL
                ORDER BY arrival_date
            """, (purchase_id,))
            points = cur.fetchall()
            cur.close()
            
            if len(points) < 2:
                return
                
            # Рисуем линии маршрута
            prev_point = None
            for point in points:
                if prev_point:
                    x1 = (prev_point['longitude'] + 180) * (Config.CANVAS_WIDTH / 360)
                    y1 = (90 - prev_point['latitude']) * (Config.CANVAS_HEIGHT / 180)
                    x2 = (point['longitude'] + 180) * (Config.CANVAS_WIDTH / 360)
                    y2 = (90 - point['latitude']) * (Config.CANVAS_HEIGHT / 180)
                    
                    self.map_canvas.create_line(x1, y1, x2, y2, fill="#FF5722", 
                                              width=3, dash=(5, 2))
                
                prev_point = point
                
        except Error as e:
            print(f"Error drawing car route: {e}")
    
    def clear_map(self):
        """Очищает карту"""
        if self.map_canvas:
            self.map_canvas.delete("all")
            
            # Перерисовываем базовое изображение карты
            if self.map_image:
                self.map_tk = ImageTk.PhotoImage(self.map_image)
                self.map_canvas.create_image(0, 0, anchor="nw", image=self.map_tk)
            else:
                self._draw_simple_map()