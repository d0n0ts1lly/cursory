import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from config.settings import Config
from utils.image_processing import create_round_avatar, create_default_avatar
from mysql.connector import Error

class UserDashboard:
    """Пользовательская панель управления"""
    
    def __init__(self, parent, connection, current_user):
        self.parent = parent
        self.conn = connection
        self.current_user = current_user
        
        self.left_frame = None
        self.center_frame = None
        self.right_frame = None
        self.cars_list = None
        self.user_cars = []
        self.search_var = None
        
        self._build_dashboard()
    
    def _build_dashboard(self):
        """Построение пользовательской панели"""
        # Left sidebar - cars list
        self.left_frame = tb.Frame(self.parent, width=320)
        self.left_frame.pack(side="left", fill="y", padx=(0,10))

        # Main content - map and details
        self.center_frame = tb.Frame(self.parent)
        self.center_frame.pack(side="left", fill="both", expand=True)

        # Right sidebar - actions and gallery
        self.right_frame = tb.Frame(self.parent, width=300)
        self.right_frame.pack(side="right", fill="y", padx=(10,0))

        self._build_user_sidebar()
        self._build_user_center()
        self._build_user_right()
        self._load_user_cars()
    
    def _build_user_sidebar(self):
        """Улучшенный сайдбар пользователя"""
        # User profile card
        profile_frame = tb.Frame(self.left_frame, bootstyle="light")
        profile_frame.pack(fill="x", padx=5, pady=5)

        # Try to load user avatar
        avatar_path = Config.get_user_avatar_path(self.current_user['id'])
        if avatar_path.exists():
            avatar_img = Image.open(avatar_path)
            avatar_img = create_round_avatar(avatar_img)
        else:
            # Create default avatar
            avatar_img = create_default_avatar()
            
        avatar_tk = ImageTk.PhotoImage(avatar_img)
        avatar_label = tb.Label(profile_frame, image=avatar_tk)
        avatar_label.image = avatar_tk
        avatar_label.pack(pady=10)

        tb.Label(profile_frame, text=self.current_user['username'], 
                font=("Segoe UI", 14, "bold")).pack()
        tb.Label(profile_frame, text=f"ID: {self.current_user['id']}", 
                font=("Segoe UI", 10), bootstyle="secondary").pack()

        # Cars list with search
        search_frame = tb.Frame(self.left_frame)
        search_frame.pack(fill="x", padx=5, pady=5)

        tb.Label(search_frame, text="Мої авто", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        
        self.search_var = tb.StringVar()
        search_entry = tb.Entry(search_frame, textvariable=self.search_var, 
                               placeholder="Пошук по VIN або моделі...")
        search_entry.pack(fill="x", pady=5)
        search_entry.bind("<KeyRelease>", self._filter_cars_list)

        # Enhanced cars list
        list_frame = tb.Frame(self.left_frame)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.cars_list = ttk.Treeview(list_frame, show="tree", height=20)
        self.cars_list.pack(fill="both", expand=True)
        self.cars_list.bind("<<TreeviewSelect>>", self._on_car_select)

        # Control buttons
        btn_frame = tb.Frame(self.left_frame)
        btn_frame.pack(fill="x", padx=5, pady=5)

        tb.Button(btn_frame, text="🔄 Оновити", bootstyle="info", 
                 command=self._load_user_cars).pack(side="left", fill="x", expand=True, padx=2)
        tb.Button(btn_frame, text="➕ Додати авто", bootstyle="success", 
                 command=self._add_new_car).pack(side="left", fill="x", expand=True, padx=2)
    
    def _build_user_center(self):
        """Центральная область с картой и деталями"""
        # Top card with car info
        self.info_card = tb.Frame(self.center_frame, bootstyle="light", padding=15)
        self.info_card.pack(fill="x", pady=(0,10))

        # Car image and basic info will be populated when car is selected
        self._create_empty_info_card()

        # Timeline
        self.timeline_frame = tb.Frame(self.center_frame)
        self.timeline_frame.pack(fill="x", pady=10)

        # Map area will be created by the main app
        self.map_container = tb.Frame(self.center_frame)
        self.map_container.pack(fill="both", expand=True, pady=10)
    
    def _create_empty_info_card(self):
        """Создает пустую карточку информации об авто"""
        for w in self.info_card.winfo_children():
            w.destroy()

        # Image placeholder
        img_frame = tb.Frame(self.info_card)
        img_frame.pack(side="left", padx=10)

        self.car_image_lbl = tb.Label(img_frame, text="🚗", font=("Segoe UI", 48),
                                     bootstyle="secondary")
        self.car_image_lbl.pack()

        # Info placeholder
        info_frame = tb.Frame(self.info_card)
        info_frame.pack(side="left", fill="x", expand=True)

        self.lbl_vin = tb.Label(info_frame, text="Оберіть авто зі списку", 
                               font=("Segoe UI", 16, "bold"))
        self.lbl_vin.pack(anchor="w", pady=2)

        self.lbl_make = tb.Label(info_frame, text="—", font=("Segoe UI", 12))
        self.lbl_make.pack(anchor="w", pady=1)

        self.lbl_status = tb.Label(info_frame, text="—", font=("Segoe UI", 11))
        self.lbl_status.pack(anchor="w", pady=1)
    
    def _build_user_right(self):
        """Правая панель с действиями и галереей"""
        tb.Label(self.right_frame, text="Дії", 
                font=("Segoe UI", 14, "bold")).pack(pady=10)

        actions = [
            ("🖼️ Галерея фото", "outline-primary", self._show_gallery),
            ("📋 Детальна інформація", "outline-info", self._show_detailed_info),
            ("📞 Зв'язатися", "outline-success", self._contact_support),
            ("🔄 Оновити статус", "outline-warning", self._load_user_cars),
            ("📤 Експорт даних", "outline-secondary", self._export_my_data)
        ]

        for text, style, command in actions:
            btn = tb.Button(self.right_frame, text=text, bootstyle=style, 
                          command=command)
            btn.pack(fill="x", padx=10, pady=3)

        # Gallery preview
        tb.Label(self.right_frame, text="Останні фото", 
                font=("Segoe UI", 12, "bold")).pack(pady=(20,5))

        self.gallery_preview = tb.Frame(self.right_frame)
        self.gallery_preview.pack(fill="both", expand=True, padx=10, pady=5)
    
    def _load_user_cars(self):
        """Загрузка автомобилей пользователя"""
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute("""
                SELECT p.*, c.country_name, ds.status_name, ds.status_id
                FROM purchases p
                LEFT JOIN countries c ON p.country_id = c.country_id
                LEFT JOIN delivery_status ds ON p.delivery_status_id = ds.status_id
                WHERE p.buyer_id = %s 
                ORDER BY p.purchase_date DESC
            """, (self.current_user['id'],))
            rows = cur.fetchall()
            self.user_cars = rows or []
            
            # Обновляем список
            for item in self.cars_list.get_children():
                self.cars_list.delete(item)
                
            for car in self.user_cars:
                status = car.get('status_name', 'Невідомо')
                self.cars_list.insert("", "end", iid=str(car["purchase_id"]),
                                    text=f"{car['car_make']} {car['car_model']}",
                                    values=(status,))
            cur.close()
            
        except Error as e:
            messagebox.showerror("DB Error", str(e))
    
    def _filter_cars_list(self, event=None):
        """Фильтрация списка автомобилей"""
        search_term = self.search_var.get().lower()
        
        for item in self.cars_list.get_children():
            self.cars_list.delete(item)
            
        for car in self.user_cars:
            vin = car.get('vin_number', '').lower()
            make = car.get('car_make', '').lower()
            model = car.get('car_model', '').lower()
            
            if (search_term in vin or search_term in make or search_term in model):
                status_name = self._get_status_name(car.get("delivery_status_id"))
                self.cars_list.insert("", "end", iid=str(car["purchase_id"]),
                                    text=f"{car['car_make']} {car['car_model']}",
                                    values=(status_name,))
    
    def _on_car_select(self, event=None):
        """Обработка выбора автомобиля"""
        sel = self.cars_list.selection()
        if not sel:
            return
        pid = int(sel[0])
        purchase = next((p for p in self.user_cars if p["purchase_id"] == pid), None)
        if not purchase:
            return
        
        # Вызываем callback из основного приложения
        if hasattr(self.parent, 'on_car_select'):
            self.parent.on_car_select(purchase)
    
    def _add_new_car(self):
        """Добавление нового автомобиля"""
        # Этот метод будет реализован в основном приложении
        pass
    
    def _show_gallery(self):
        """Показ галереи изображений"""
        sel = self.cars_list.selection()
        if not sel:
            messagebox.showwarning("Увага", "Оберіть авто зі списку")
            return

        messagebox.showinfo("Галерея", "Функція галереї в розробці")
    
    def _show_detailed_info(self):
        """Показывает детальную информацию о выбранном авто"""
        sel = self.cars_list.selection()
        if not sel:
            messagebox.showwarning("Увага", "Оберіть авто зі списку")
            return

        # Этот метод будет реализован в основном приложении
        pass
    
    def _contact_support(self):
        """Контакт с поддержкой"""
        contact_win = tb.Toplevel(self.parent)
        contact_win.title("Зв'язатися з підтримкою")
        contact_win.geometry("400x300")

        tb.Label(contact_win, text="Контактна інформація", 
                font=("Segoe UI", 16, "bold")).pack(pady=20)

        contacts = [
            ("📞 Телефон", "+380 12 345 6789"),
            ("📧 Email", "support@autotracker.com"),
            ("🌐 Веб-сайт", "www.autotracker.com"),
            ("🕒 Години роботи", "Пн-Пт: 9:00-18:00")
        ]

        for icon, info in contacts:
            frame = tb.Frame(contact_win)
            frame.pack(fill="x", pady=8, padx=20)
            tb.Label(frame, text=icon, font=("Segoe UI", 14)).pack(side="left")
            tb.Label(frame, text=info, font=("Segoe UI", 12)).pack(side="left", padx=10)
    
    def _export_my_data(self):
        """Экспорт данных пользователя"""
        # Этот метод будет реализован в основном приложении
        pass
    
    def _get_status_name(self, status_id):
        """Получение названия статуса"""
        if not status_id:
            return "Невідомо"
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT status_name FROM delivery_status WHERE status_id=%s", (status_id,))
            row = cur.fetchone()
            cur.close()
            return row[0] if row else "Невідомо"
        except:
            return "Невідомо"
    
    def update_car_info(self, purchase):
        """Обновление информации об автомобиле"""
        # Обновляем основную информацию
        self.lbl_vin.config(text=f"{purchase['car_make']} {purchase['car_model']}")
        self.lbl_make.config(text=f"VIN: {purchase.get('vin_number', '—')}")
        
        status_name = purchase.get('status_name', 'Невідомо')
        status_color = "success" if "доставлено" in status_name.lower() else "warning"
        self.lbl_status.config(text=f"Статус: {status_name}", bootstyle=status_color)