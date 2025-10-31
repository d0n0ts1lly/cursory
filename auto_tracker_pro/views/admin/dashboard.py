import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox
from mysql.connector import Error

class AdminDashboard:
    """Админская панель управления"""
    
    def __init__(self, parent, connection, current_user):
        self.parent = parent
        self.conn = connection
        self.current_user = current_user
        
        self.left_frame = None
        self.center_frame = None
        self.right_frame = None
        
        self._build_dashboard()
    
    def _build_dashboard(self):
        """Построение админской панели"""
        # Left sidebar
        self.left_frame = tb.Frame(self.parent, width=280)
        self.left_frame.pack(side="left", fill="y", padx=(0,10))

        # Main content area
        self.center_frame = tb.Frame(self.parent)
        self.center_frame.pack(side="left", fill="both", expand=True)

        # Right sidebar for stats
        self.right_frame = tb.Frame(self.parent, width=300)
        self.right_frame.pack(side="right", fill="y", padx=(10,0))

        self._build_admin_sidebar()
        self._build_admin_main()
        self._build_admin_stats()
    
    def _build_admin_sidebar(self):
        """Боковая панель администратора"""
        tb.Label(self.left_frame, text="Адмін-панель", 
                font=("Segoe UI", 16, "bold")).pack(pady=20)

        # Quick stats
        stats_frame = tb.Frame(self.left_frame)
        stats_frame.pack(fill="x", padx=10, pady=10)

        try:
            cur = self.conn.cursor()
            
            # User count
            cur.execute("SELECT COUNT(*) FROM users")
            user_count = cur.fetchone()[0]
            
            # Active shipments
            cur.execute("SELECT COUNT(*) FROM purchases WHERE delivery_status_id IS NOT NULL")
            shipment_count = cur.fetchone()[0]
            
            # Countries count
            cur.execute("SELECT COUNT(*) FROM countries")
            countries_count = cur.fetchone()[0]
            
            cur.close()
            
            self._create_stat_card(stats_frame, "👥 Користувачі", user_count, "primary")
            self._create_stat_card(stats_frame, "🚚 Відправлення", shipment_count, "success")
            self._create_stat_card(stats_frame, "🌍 Країни", countries_count, "info")
            
        except Error as e:
            print(f"Error loading stats: {e}")

        # Navigation
        nav_frame = tb.Frame(self.left_frame)
        nav_frame.pack(fill="x", padx=10, pady=20)

        tables = [
            ("📊 Головна", "dashboard"),
            ("👥 Користувачі", "users"),
            ("🌍 Країни", "countries"),
            ("📦 Покупки", "purchases"),
            ("📍 Маршрути", "delivery_route_points"),
            ("🖼️ Фото", "purchase_images"),
            ("🚢 Компанії", "shipping_companies"),
            ("📈 Аналітика", "analytics"),
            ("🗺️ Управління картою", "map_management")
        ]

        for icon_text, table in tables:
            btn = tb.Button(nav_frame, text=icon_text, bootstyle="light-outline",
                          command=lambda t=table: self._admin_navigate(t))
            btn.pack(fill="x", pady=3)
    
    def _create_stat_card(self, parent, title, value, style):
        """Создает карточку статистики"""
        card = tb.Frame(parent, bootstyle=style)
        card.pack(fill="x", pady=2)
        
        tb.Label(card, text=title, font=("Segoe UI", 10), 
                bootstyle=f"inverse-{style}").pack(anchor="w", padx=10, pady=(8,2))
        tb.Label(card, text=str(value), font=("Segoe UI", 18, "bold"), 
                bootstyle=f"inverse-{style}").pack(anchor="w", padx=10, pady=(2,8))
    
    def _build_admin_main(self):
        """Основная область админ-панели"""
        # Welcome card
        welcome_card = tb.Frame(self.center_frame, bootstyle="info")
        welcome_card.pack(fill="x", pady=(0,20))
        
        tb.Label(welcome_card, text="Адміністративна панель", 
                font=("Segoe UI", 20, "bold"), bootstyle="inverse-info").pack(pady=15)

        # Quick actions
        actions_frame = tb.Frame(self.center_frame)
        actions_frame.pack(fill="x", pady=10)

        quick_actions = [
            ("➕ Додати користувача", "success", lambda: self._admin_open_table("users")),
            ("📦 Керування покупками", "warning", lambda: self._admin_open_table("purchases")),
            ("🌍 Додати країну", "info", lambda: self._admin_open_table("countries")),
            ("📊 Переглянути аналітику", "info", lambda: self._show_analytics()),
        ]

        for text, style, command in quick_actions:
            btn = tb.Button(actions_frame, text=text, bootstyle=style, command=command)
            btn.pack(side="left", padx=5, pady=5)

        # Recent activity
        self._show_recent_activity()
    
    def _build_admin_stats(self):
        """Правая панель со статистикой"""
        tb.Label(self.right_frame, text="Швидка статистика", 
                font=("Segoe UI", 14, "bold")).pack(pady=15)

        try:
            cur = self.conn.cursor()
            
            # Delivery status stats
            cur.execute("""
                SELECT ds.status_name, COUNT(p.purchase_id) as count
                FROM delivery_status ds
                LEFT JOIN purchases p ON ds.status_id = p.delivery_status_id
                GROUP BY ds.status_id, ds.status_name
                ORDER BY ds.order_index
            """)
            status_stats = cur.fetchall()
            cur.close()

            for status_name, count in status_stats:
                self._create_mini_stat(self.right_frame, status_name, count, "secondary")
                
        except Error as e:
            print(f"Error loading status stats: {e}")
    
    def _create_mini_stat(self, parent, label, value, style):
        """Мини-карточка статистики"""
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=5, padx=10)
        
        tb.Label(frame, text=label, font=("Segoe UI", 10)).pack(side="left")
        tb.Label(frame, text=str(value), font=("Segoe UI", 12, "bold"), 
                bootstyle=style).pack(side="right")
    
    def _admin_navigate(self, destination):
        """Навигация в админ-панели"""
        # Этот метод будет реализован в основном приложении
        pass
    
    def _admin_open_table(self, table):
        """Открытие таблицы для админа"""
        # Этот метод будет реализован в основном приложении
        pass
    
    def _show_analytics(self):
        """Показ аналитики"""
        # Этот метод будет реализован в основном приложении
        pass
    
    def _show_recent_activity(self):
        """Показывает последнюю активность"""
        activity_frame = tb.Frame(self.center_frame)
        activity_frame.pack(fill="both", expand=True, pady=10)

        tb.Label(activity_frame, text="Остання активність", 
                font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute("""
                SELECT u.username, p.car_make, p.car_model, ds.status_name,
                       p.purchase_date
                FROM purchases p
                JOIN users u ON p.buyer_id = u.id
                LEFT JOIN delivery_status ds ON p.delivery_status_id = ds.status_id
                ORDER BY p.purchase_date DESC
                LIMIT 10
            """)
            activities = cur.fetchall()
            cur.close()

            for activity in activities:
                self._create_activity_item(activity_frame, activity)

        except Error as e:
            tb.Label(activity_frame, text=f"Помилка завантаження активності: {e}").pack()
    
    def _create_activity_item(self, parent, activity):
        """Создает элемент активности"""
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=3, padx=10)
        
        text = f"{activity['username']} - {activity['car_make']} {activity['car_model']}"
        tb.Label(frame, text=text, font=("Segoe UI", 10)).pack(side="left")
        tb.Label(frame, text=activity['status_name'], 
                bootstyle="success").pack(side="right", padx=5)
        tb.Label(frame, text=activity['purchase_date'].strftime("%d.%m.%Y"), 
                font=("Segoe UI", 9), bootstyle="secondary").pack(side="right")