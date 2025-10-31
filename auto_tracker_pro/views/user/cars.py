import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox
from mysql.connector import Error
from views.components.dialogs import ModernCRUDDialog

class CarManager:
    """Менеджер для работы с автомобилями пользователя"""
    
    def __init__(self, parent, connection, current_user):
        self.parent = parent
        self.conn = connection
        self.current_user = current_user
    
    def add_new_car(self, on_success_callback=None):
        """Добавление нового автомобиля"""
        def save_car(data, mode):
            try:
                data['buyer_id'] = self.current_user['id']
                cur = self.conn.cursor()
                columns = ', '.join([f"`{k}`" for k in data.keys()])
                placeholders = ', '.join(['%s'] * len(data))
                sql = f"INSERT INTO purchases ({columns}) VALUES ({placeholders})"
                cur.execute(sql, tuple(data.values()))
                self.conn.commit()
                cur.close()
                messagebox.showinfo("Успіх", "Автомобіль додано успішно!")
                if on_success_callback:
                    on_success_callback()
            except Error as e:
                messagebox.showerror("Помилка", f"Помилка додавання: {e}")

        ModernCRUDDialog(self.parent, "Додати нове авто", "purchases", "add", on_save=save_car)
    
    def show_detailed_info(self, purchase):
        """Показывает детальную информацию о выбранном авто"""
        detail_win = tb.Toplevel(self.parent)
        detail_win.title(f"Детальна інформація - {purchase['car_make']} {purchase['car_model']}")
        detail_win.geometry("600x700")

        # Создаем notebook для вкладок
        notebook = tb.Notebook(detail_win)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Основная информация
        info_frame = tb.Frame(notebook)
        notebook.add(info_frame, text="Основна інформація")

        fields = [
            ("VIN номер", purchase.get('vin_number', '—')),
            ("Марка", purchase.get('car_make', '—')),
            ("Модель", purchase.get('car_model', '—')),
            ("Рік", purchase.get('car_year', '—')),
            ("Колір", purchase.get('car_color', '—')),
            ("Ціна", purchase.get('price', '—')),
            ("Дата покупки", purchase.get('purchase_date', '—')),
            ("Очікувана дата прибуття", purchase.get('estimated_arrival_date', '—')),
            ("Країна походження", purchase.get('country_name', '—'))
        ]

        for i, (label, value) in enumerate(fields):
            row = tb.Frame(info_frame)
            row.pack(fill="x", pady=5, padx=10)
            tb.Label(row, text=label, font=("Segoe UI", 10, "bold"), 
                    width=25, anchor="w").pack(side="left")
            tb.Label(row, text=str(value), font=("Segoe UI", 10)).pack(side="left")

        # История статусов
        history_frame = tb.Frame(notebook)
        notebook.add(history_frame, text="Історія статусів")
        
        # Загружаем историю статусов
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute("""
                SELECT ds.status_name, ds.description, p.updated_at
                FROM purchase_status_history p
                JOIN delivery_status ds ON p.status_id = ds.status_id
                WHERE p.purchase_id = %s
                ORDER BY p.updated_at DESC
            """, (purchase['purchase_id'],))
            history = cur.fetchall()
            cur.close()
            
            if history:
                for i, record in enumerate(history):
                    history_row = tb.Frame(history_frame)
                    history_row.pack(fill="x", pady=3, padx=10)
                    
                    tb.Label(history_row, text=record['status_name'], 
                            font=("Segoe UI", 10, "bold")).pack(anchor="w")
                    tb.Label(history_row, text=record['description'], 
                            font=("Segoe UI", 9)).pack(anchor="w")
                    tb.Label(history_row, 
                            text=record['updated_at'].strftime("%d.%m.%Y %H:%M"),
                            font=("Segoe UI", 8), bootstyle="secondary").pack(anchor="w")
            else:
                tb.Label(history_frame, text="Історія статусів відсутня",
                        font=("Segoe UI", 11), bootstyle="secondary").pack(pady=20)
                
        except Error as e:
            tb.Label(history_frame, text=f"Помилка завантаження історії: {e}",
                    font=("Segoe UI", 10), bootstyle="danger").pack(pady=20)
    
    def export_user_data(self, user_id):
        """Экспорт данных пользователя"""
        from utils.helpers import export_to_csv
        
        query = """
            SELECT p.*, c.country_name, ds.status_name
            FROM purchases p
            LEFT JOIN countries c ON p.country_id = c.country_id
            LEFT JOIN delivery_status ds ON p.delivery_status_id = ds.status_id
            WHERE p.buyer_id = %s
        """
        
        export_to_csv(self.conn, query, f"my_cars_{user_id}.csv", (user_id,))